
from typing import Union, TypeVar, Generic, Callable,Optional

from ..backend import TensorLike
from ..backend import backend_manager as bm
from .space import FunctionSpace
from .bernstein_fe_space import BernsteinFESpace  
from .function import Function

from scipy.sparse import csr_matrix
from ..mesh.mesh_base import Mesh
from ...decorator import barycentric, cartesian

_MT = TypeVar('_MT', bound=Mesh)
Index = Union[int, slice, TensorLike]
Number = Union[int, float]
_S = slice(None)

# 自由度管理
class FirstNedelecDof2d():
    def __init__(self, mesh, p):
        self.p = p
        self.mesh = mesh
        self.multiindex = mesh.multi_index_matrix(p,2)
        self.ftype = mesh.ftype
        self.itype = mesh.itype

    def number_of_local_dofs(self,doftype ='all'):
        p = self.p
        if doftype == 'all':
            return (p+1)*(p+3)
        elif doftype in {'cell', 2}:
            return (p+1)*p
        elif doftype in {'face','edge', 1}:
            return p+1
        elif doftype in {'node',0}:
            return 0

    def number_of_global_dofs(self):
        NC =  self.mesh.number_of_cells()
        NE =  self.mesh.number_of_edges()
        edof = self.number_of_local_dofs("edge")
        cdof = self.number_of_local_dofs("cell")
        return NE*edof + NC*cdof

    def edge_to_dof(self,index = _S):
        NE = self.mesh.number_of_edges()
        edof = self.number_of_local_dofs("edge") 
        return bm.arange(NE*edof).reshape(NE,edof)[index]

    def cell_to_dof(self):
        p = self.p
        cldof = self.number_of_local_dofs('cell')
        eldof = self.number_of_local_dofs('edge')
        ldof = self.number_of_local_dofs()
        gdof = self.number_of_global_dofs()
        e2dof = self.edge_to_dof()

        NC = self.mesh.number_of_cells()
        NE = self.mesh.number_of_edges()
        c2e = self.mesh.cell_to_edge()
        edge = self.mesh.entity('edge')
        cell = self.mesh.entity('cell')

        c2d = bm.zeros((NC, ldof), dtype=self.itype)
        c2d[:, :eldof*3] = e2dof[c2e].reshape(NC, eldof*3)
        s = [1, 0, 0]
        for i in range(3):
            flag = cell[:, s[i]] == edge[c2e[:, i], 1]   
            c2d[flag, eldof*i:eldof*(i+1)] = bm.flip(c2d[flag, eldof*i:eldof*(i+1)],axis=-1)
        c2d[:, eldof*3:] = bm.arange(NE*eldof, gdof).reshape(NC, -1)
        return c2d
    
    @property
    def cell2dof(self):
        return self.cell_to_dof()

    def boundary_dof(self):
        eidx = self.mesh.boundary_face_index()
        e2d = self.edge_to_dof(index=eidx)
        return e2d.reshape(-1)

    def is_boundary_dof(self):
        bddof = self.boundary_dof()

        gdof = self.number_of_global_dofs()
        flag = bm.zeros(gdof, dtype=bm.bool)

        flag[bddof] = True
        return flag


class FirstNedelecFiniteElementSpace2d(FunctionSpace, Generic[_MT]):
    def __init__(self, mesh, p):
        self.p = p
        self.mesh = mesh
        self.dof = FirstNedelecDof2d(mesh, p)

        self.bspace = BernsteinFESpace(mesh, p)
        self.cellmeasure = mesh.entity_measure('cell')
        self.qf = self.mesh.quadrature_formula(p+3)
        self.ftype = mesh.ftype
        self.itype = mesh.itype

    @barycentric
    def basis(self, bcs, index=_S):
        p = self.p
        mesh = self.mesh
        NC = mesh.number_of_cells()    
        GD = mesh.geo_dimension()      
        ldof = self.dof.number_of_local_dofs()  
        cldof = self.dof.number_of_local_dofs("cell")  
        eldof = self.dof.number_of_local_dofs("edge")  
        gdof = self.dof.number_of_global_dofs()         
        glambda = mesh.grad_lambda()    
        ledge = mesh.localEdge       

        c2esign = mesh.cell_to_edge_sign() 

        l = bm.zeros((3, )+bcs[None, :,0, None, None].shape, dtype=self.ftype)
        l[0] = bcs[None, :,0,  None, None]
        l[1] = bcs[None, :,1,  None, None]
        l[2] = bcs[None, :,2,  None, None] 
                                           
        # edge basis
        phi = self.bspace.basis(bcs, p=p)
        multiIndex = self.mesh.multi_index_matrix(p, 2)
        val = bm.zeros((NC,) + bcs.shape[:-1]+(ldof, 2), dtype=self.ftype)
        for i in range(3):
            phie = phi[:, :, multiIndex[:, i]==0] 
            c2esi = c2esign[:, i]
            v = l[ledge[i, 0]]*glambda[:,None, ledge[i, 1], None,:] - l[ledge[i, 1]]*glambda[:,None, ledge[i, 0], None,:]   
            v[~c2esi, :,  :, :] *= -1 
            val[..., eldof*i:eldof*(i+1), :] = phie[..., None]*v

        # cell basis
        if(p > 0):
            phi = self.bspace.basis(bcs, p=p-1) 
            v0 = l[2]*(l[0]*glambda[:,None, 1, None] - l[1]*glambda[:,None, 0, None]) 
            v1 = l[0]*(l[1]*glambda[:,None, 2, None] - l[2]*glambda[:,None, 1, None])
            val[..., eldof*3:eldof*3+cldof//2, :] = v0*phi[..., None] 
            val[..., eldof*3+cldof//2:, :] = v1*phi[..., None] 
        return val[index]

    def cross2d(self,a,b):
        return a[...,0]*b[...,1] - a[...,1]*b[...,0]

    @barycentric
    def curl_basis(self, bcs):
        p = self.p
        mesh = self.mesh
        NC = mesh.number_of_cells()
        GD = mesh.geo_dimension()
        ldof = self.dof.number_of_local_dofs()
        cldof = self.dof.number_of_local_dofs("cell")
        eldof = self.dof.number_of_local_dofs("edge")
        gdof = self.dof.number_of_global_dofs()
        glambda = mesh.grad_lambda()
        ledge = mesh.localEdge

        c2esign = mesh.cell_to_edge_sign() 

        l = bm.zeros((3, )+bcs[None,:, 0, None, None].shape, dtype=self.ftype)
        l[0] = bcs[None, :,0, None, None]
        l[1] = bcs[None,:, 1, None, None]
        l[2] = bcs[None,:, 2, None, None]

        # edge basis
        phi = self.bspace.basis(bcs, p=p)
        gphi = self.bspace.grad_basis(bcs, p=p)
        multiIndex = self.mesh.multi_index_matrix(p, 2)
        val = bm.zeros((NC,) + bcs.shape[:-1]+(ldof,), dtype=self.ftype)
        for i in range(3):
            phie = phi[..., multiIndex[:, i]==0]
            gphie = gphi[..., multiIndex[:, i]==0, :]
            c2esi = c2esign[:, i]
            v = l[ledge[i, 0]]*glambda[:,None, ledge[i, 1], None] - l[ledge[i, 1]]*glambda[:,None, ledge[i, 0], None]
            v[~c2esi,:, :, :] *= -1 
            cv = 2*self.cross2d(glambda[:,None, ledge[i, 0],None], glambda[:,None, ledge[i, 1],None])
            cv[~c2esi] *= -1
            val[..., eldof*i:eldof*(i+1)] = phie*cv + self.cross2d(gphie, v)

        # cell basis
        if(p > 0):
            phi = self.bspace.basis(bcs, p=p-1)
            gphi = self.bspace.grad_basis(bcs, p=p-1)


            w0 = l[0]*glambda[:,None, 1, None] - l[1]*glambda[:,None, 0, None]
            w1 = l[1]*glambda[:,None, 2, None] - l[2]*glambda[:,None, 1, None]
            cw0 = 2*self.cross2d(glambda[:,None, 0, None], glambda[:,None, 1, None]) 
            cw1 = 2*self.cross2d(glambda[:,None, 1, None], glambda[:,None, 2, None])

            v0 = l[2]*w0
            v1 = l[0]*w1
            cv0 = self.cross2d(glambda[:,None, 2, None], w0) + l[2, ..., 0]*cw0 #(NQ, NC, ldof)
            cv1 = self.cross2d(glambda[:,None,0, None], w1) + l[0, ..., 0]*cw1

            val[..., eldof*3:eldof*3+cldof//2] = self.cross2d(gphi, v0) + phi*cv0 
            val[..., eldof*3+cldof//2:] = self.cross2d(gphi, v1) + phi*cv1 
        return val

    def is_boundary_dof(self, threshold=None):
        return self.dof.is_boundary_dof()

    def cell_to_dof(self):
        return self.dof.cell2dof

    def number_of_global_dofs(self):
        return self.dof.number_of_global_dofs()

    def number_of_local_dofs(self, doftype='all'):
        return self.dof.number_of_local_dofs(doftype)

    @barycentric
    def value(self, uh, bcs, index=_S):
        '''@
        @brief 计算一个有限元函数在每个单元的 bc 处的值
        @param bc : (..., GD+1)
        @return val : (..., NC, GD)
        '''
        phi = self.basis(bcs)
        c2d = self.dof.cell_to_dof()
        # uh[c2d].shape = (NC, ldof); phi.shape = (..., NC, ldof, GD)
        val = bm.einsum("cl, cqlk->cqk", uh[c2d], phi)
        return val

    @barycentric
    def curl_value(self, uh, bcs, index=_S):
        '''@
        @brief 计算一个有限元函数在每个单元的 bc 处的值
        @param bc : (..., GD+1)
        @return val : (..., NC, GD)
        '''
        cphi = self.curl_basis(bcs)
        c2d = self.dof.cell_to_dof()
        # uh[c2d].shape = (NC, ldof); phi.shape = (..., NC, ldof, GD)
        val = bm.einsum("cl, cql->cq", uh[c2d], cphi)
        return val

    @barycentric
    def div_value(self, uh, bc, index=_S):
        pass

    @barycentric
    def grad_value(self, uh, bc, index=_S):
        pass

    @barycentric
    def edge_value(self, uh, bc, index=_S):
        pass

    @barycentric
    def face_value(self, uh, bc, index=_S):
        pass

    def mass_matrix(self):
        mesh = self.mesh
        NC = mesh.number_of_cells()
        ldof = self.dof.number_of_local_dofs()
        gdof = self.dof.number_of_global_dofs()
        cm = self.cellmeasure
        c2d = self.dof.cell_to_dof()

        bcs, ws = self.qf.get_quadrature_points_and_weights()
        phi = self.basis(bcs)
        mass = bm.einsum("cqlg, cqdg, c, q->cld", phi, phi, cm, ws)

        I = bm.broadcast_to(c2d[:, :, None], mass.shape).reshape(-1)
        J = bm.broadcast_to(c2d[:, None, :], mass.shape).reshape(-1)
        I = bm.to_numpy(I)
        J = bm.to_numpy(J)
        mass = bm.to_numpy(mass).reshape(-1)
        M = csr_matrix((mass, (I, J)), shape=(gdof, gdof))
        return M 

    def curl_matrix(self):
        mesh = self.mesh
        NC = mesh.number_of_cells()
        ldof = self.dof.number_of_local_dofs()
        gdof = self.dof.number_of_global_dofs()
        cm = self.cellmeasure

        c2d = self.dof.cell_to_dof()
        bcs, ws = self.qf.get_quadrature_points_and_weights()

        cphi = self.curl_basis(bcs) 
        A = bm.einsum("cql, cqd, c, q->cld", cphi, cphi, cm, ws)

        I = bm.broadcast_to(c2d[:, :, None], A.shape).reshape(-1)
        J = bm.broadcast_to(c2d[:, None, :], A.shape).reshape(-1)
        I = bm.to_numpy(I)
        J = bm.to_numpy(J)
        A = bm.to_numpy(A).reshape(-1)
        B = csr_matrix((A, (I, J)), shape=(gdof, gdof))
        return B

    def source_vector(self, f):
        mesh = self.mesh
        cm = self.cellmeasure
        ldof = self.dof.number_of_local_dofs()
        gdof = self.dof.number_of_global_dofs()
        bcs, ws = self.qf.get_quadrature_points_and_weights()
        c2d = self.dof.cell_to_dof()

        p = mesh.bc_to_point(bcs) 
        fval = f(p) 

        phi = self.basis(bcs) 
        val = bm.einsum("cqg, cqlg, q, c->cl", fval, phi, ws, cm)# (NC, ldof)
        vec = bm.zeros(gdof, dtype=self.ftype)
        bm.scatter_add(vec, c2d.reshape(-1), val.reshape(-1))
        return vec

    def set_dirichlet_bc(self, gD, uh, threshold=None, q=None):
        p = self.p
        mesh = self.mesh
        ldof = p+1
        gdof = self.number_of_global_dofs()

        index = self.mesh.boundary_face_index()

        edge2dof = self.dof.edge_to_dof()[index]
        uh[edge2dof] = 0

        isDDof = bm.zeros(gdof, dtype=bm.bool)
        isDDof[edge2dof] = True
        return isDDof

    boundary_interpolate = set_dirichlet_bc
    
    # def projection(self, f, method="L2"):
    #     M = self.mass_matrix()
    #     b = self.source_vector(f)
    #     x = spsolve(M, b)
    #     return self.function(array=x)


    # def interplation(self, f):
    #     """
    #     @brief ERROR TODO
    #     """
    #     mesh = self.mesh
    #     node = mesh.entity("node")
    #     edge = mesh.entity("edge")

    #     gdof = self.dof.number_of_global_dofs()
    #     e2n = mesh.edge_unit_normal()
    #     val = bm.zeros(gdof, dtype=self.ftype)

    #     f0 = f(node[edge[:, 0]]) 
    #     f1 = f(node[edge[:, 1]])

    #     val[0::2] = bm.sum(f0*e2n, axis=1)
    #     val[1::2] = bm.sum(f1*e2n, axis=1)
    #     return function(array=val)

