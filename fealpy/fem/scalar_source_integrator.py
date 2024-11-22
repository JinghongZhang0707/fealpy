from typing import Optional, Literal

from ..backend import backend_manager as bm
from ..typing import TensorLike, Index, _S, SourceLike

from ..mesh import HomogeneousMesh
from ..functionspace.space import FunctionSpace as _FS
from ..utils import process_coef_func
from ..functional import linear_integral
from .integrator import LinearInt, SrcInt, CellInt, enable_cache, assemblymethod


class ScalarSourceIntegrator(LinearInt, SrcInt, CellInt):
    r"""The domain source integrator for function spaces based on homogeneous meshes."""
    def __init__(self, source: Optional[SourceLike]=None, q: int=None, *,
                 index: Index=_S,
                 batched: bool=False,
                 method: Literal['isopara', None] = None) -> None:
        super().__init__(method=method if method else 'assembly')
        self.source = source
        self.q = q
        self.index = index
        self.batched = batched

    @enable_cache
    def to_global_dof(self, space: _FS) -> TensorLike:
        return space.cell_to_dof()[self.index]

    @enable_cache
    def fetch(self, space: _FS):
        q = self.q
        index = self.index
        mesh = getattr(space, 'mesh', None)

        if not isinstance(mesh, HomogeneousMesh):
            raise RuntimeError("The ScalarSourceIntegrator only support spaces on"
                               f"homogeneous meshes, but {type(mesh).__name__} is"
                               "not a subclass of HomoMesh.")

        cm = mesh.entity_measure('cell', index=index)
        q = space.p+3 if self.q is None else self.q
        qf = mesh.quadrature_formula(q, 'cell')
        bcs, ws = qf.get_quadrature_points_and_weights()
        phi = space.basis(bcs, index=index)

        return bcs, ws, phi, cm, index

    def assembly(self, space: _FS) -> TensorLike:
        f = self.source
        mesh = getattr(space, 'mesh', None)
        bcs, ws, phi, cm, index = self.fetch(space)

        val = process_coef_func(f, bcs=bcs, mesh=mesh, etype='cell', index=index)
        return linear_integral(phi, ws, cm, val, batched=self.batched)

    @assemblymethod('isopara')
    def isopara_assembly(self, space: _FS) -> TensorLike: 
        f = self.source
        mesh = getattr(space, 'mesh', None)
        bcs, ws, phi, cm, index = self.fetch(space)

        rm = space.mesh.reference_cell_measure()
        G = space.mesh.first_fundamental_form(bcs)
        d = bm.sqrt(bm.linalg.det(G))

        val = process_coef_func(f, bcs=bcs, mesh=mesh, etype='cell', index=index)
        M = bm.einsum('q, cq, cql, cq -> cl', ws*rm, val, phi, d)
        return M
