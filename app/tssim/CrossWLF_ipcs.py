#!/usr/bin/python3
'''!    	
	@Author: wpx
	@File Name: cross.py
	@Mail: wpx15673207315@gmail.com 
	@Created Time: Sat 18 May 2024 03:01:14 PM CST
	@bref 
	@ref 
'''  
import numpy as np
from CrossWLFSimulator import CrossSolver
from CrossWLFModel import CrossWLF
from fealpy.mesh import TriangleMesh
from fealpy.cfd import NSFEMSolver
from fealpy.levelset.ls_fem_solver import LSFEMSolver
from fealpy.functionspace import LagrangeFESpace
from fealpy.timeintegratoralg import UniformTimeLine
from fealpy.fem import DirichletBC
import matplotlib.pyplot as plt
from fealpy.decorator import barycentric, cartesian
from scipy.sparse import csr_matrix, spdiags, eye, bmat
from scipy.sparse.linalg import spsolve

ns = 10
T = 10
nt = 2000

pde = CrossWLF()
mesh = TriangleMesh.from_box(pde.box, 10*ns, ns)
uspace = LagrangeFESpace(mesh, p=2, doforder='sdofs')
pspace = LagrangeFESpace(mesh, p=1, doforder='sdofs')
Tspace = LagrangeFESpace(mesh, p=2, doforder='sdofs')
phispace = LagrangeFESpace(mesh, p=2, doforder='sdofs')
solver  = CrossSolver(pde, mesh, uspace,pspace, phispace)
timeline = UniformTimeLine(0,T,nt)
dt = timeline.dt
LSSolver = LSFEMSolver(phispace)
NSSolver = NSFEMSolver(mesh, dt ,uspace, pspace, Tspace=Tspace) 
inletdof = uspace.is_boundary_dof(pde.is_inlet_boundary)
walldof = uspace.is_boundary_dof(pde.is_wall_boundary)

phi0 = phispace.interpolate(pde.init_surface)
phi1 = phispace.function()
u0 = uspace.function(dim=2)
us = uspace.function(dim=2)
u1 = uspace.function(dim=2)
u0[0,inletdof] = 5
p0 = pspace.function()
p1 = pspace.function()
T0 = Tspace.function()
T1 = Tspace.function()
T0[inletdof] = 525


#ipcs_0的边界处理
ubdof = uspace.is_boundary_dof(pde.is_wall_boundary) \
        | uspace.is_boundary_dof(pde.is_left_boundary)
mesh.nodedata['u0'] = u0.transpose(1,0)
u_inlet_bdof = uspace.is_boundary_dof(pde.is_inlet_boundary)
is_u_bdof = np.hstack([ubdof, ubdof])
ugdof = 2*uspace.number_of_global_dofs()
uxx = uspace.function(dim=2)
uxx[0,:][u_inlet_bdof] = 5
bdIdx = np.zeros(ugdof, dtype=np.int_)
bdIdx[is_u_bdof] = 1
uD0 = spdiags(1-bdIdx, 0, ugdof, ugdof)
uD1 = spdiags(bdIdx, 0, ugdof, ugdof)
#ipcs_1的边界处理
pbc = DirichletBC(pspace, pde.boundary_pressure, pde.is_outflow_boundary) 
#能量方程的边界处理


for i in range(1):
    phi1[:] = phi0
    #phi1[:] = LSSolver.mumps_solve(5, phi0, dt, u0)
    
    #eta_l = solver.eta_l(T0, p0, u0) 
    
    rho = solver.parfunction(pde.rho, phi1)
    C = solver.parfunction(pde.c, phi1)
    lam = solver.parfunction(pde.lam, phi1)
    #eta = solver.parfunction(eta_l/pde.eta_g, phi1)
    #netwon流情况
    eta = solver.parfunction(0.001, phi1)
    
    #Re = solver.Re(eta_l)
    Re = 0.01
    #Br = solver.Br(eta_l)
    Br = 147398.844

    delta = solver.delta_epsion(phi1)
    kappa = solver.kappa(phi1)
    
    #ipcs_0
    @barycentric
    def source(bcs, index=None):
        result = 1/pde.WE*kappa(bcs)*delta(bcs)
        result = np.einsum('ij,ijk->ijk', result, phi1.grad_value(bcs))
        return result.transpose(0,2,1)

    A0 = NSSolver.ipcs_A_0(mu=eta, rho=rho, threshold=pde.is_outflow_boundary, Re=Re)
    b0 = NSSolver.ipcs_b_0(un=u0, p0=p0, source=source, Re=Re, rho=rho, threshold=pde.is_outflow_boundary)
    b0 = b0 - A0@uxx.flatten()     
    A0 = uD0@A0@uD0 + uD1
    b0[is_u_bdof] = uxx.flatten()[is_u_bdof]
    us[:] = spsolve(A0, b0).reshape(2,-1)
    
    #ipcs_1
    A1 = NSSolver.ipcs_A_1()
    b1 = NSSolver.ipcs_b_1(us, p0, rho)
    A1,b1 = pbc.apply(A1,b1)
    p1[:] = spsolve(A1, b1)
    
    #ipcs_2
    A2 = NSSolver.ipcs_A_2(rho) 
    b2 = NSSolver.ipcs_b_2(us, p1, p0, rho)
    b2 = b2 - A2@uxx.flatten()     
    A2 = uD0@A2@uD0 + uD1
    b2[is_u_bdof] = uxx.flatten()[is_u_bdof]
    u1[:] = spsolve(A2,b2).reshape((2,-1))
    
    #tempture
    #A3 = NSSolver.temperature_A(u1, C, rho, lam, pde.Pe) 
    #b3 = NSSolver.temperature_b(T0, u1, p1, eta, Br, pde.Pe, rho, C) 

fname = 'test' + 'test_.vtu'
mesh.nodedata['u0'] = u0.transpose(1,0)
mesh.nodedata['us'] = us.transpose(1,0)
mesh.nodedata['u1'] = u1.transpose(1,0)
mesh.nodedata['p1'] = p1
mesh.nodedata['phi1'] = phi1
mesh.nodedata['phi0'] = phi0
mesh.nodedata['rho'] = rho
mesh.to_vtk(fname=fname)


'''
fig = plt.figure()
axes = fig.gca()
mesh.add_plot(axes)
mesh.find_node(axes,node=mesh.interpolation_points(p=2)[walldof],color='r')
#plt.show()
'''
