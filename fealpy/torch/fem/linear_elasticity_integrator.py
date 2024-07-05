from typing import Optional

import numpy as np
import torch
from torch import Tensor


from .utils import shear_strain, normal_strain
from ..utils import process_coef_func
from ..functionspace.utils import flatten_indices


from ..mesh import HomogeneousMesh
from ..functionspace.space import FunctionSpace as _FS
from .integrator import (
    CellOperatorIntegrator,
    enable_cache,
    assemblymethod,
    _S, Index, CoefLike
)

class LinearElasticityIntegrator(CellOperatorIntegrator):
    """
    The linear elasticity integrator for function spaces based on homogeneous meshes.
    """
    def __init__(self, 
                 lam: Optional[float]=None, mu: Optional[float]=None,
                 e: Optional[float]=None, nu: Optional[float]=None, 
                 elasticity_type: Optional[str]='stress',
                 device: Optional[torch.device]=torch.device('cpu'),
                 coef: Optional[CoefLike]=None, q: int=3, *,
                 index: Index=_S,
                 batched: bool=False,
                 method: Optional[str]=None) -> None:
        method = 'assembly' if (method is None) else method
        super().__init__(method=method)
        if lam is not None and mu is not None:
            self.e = mu * (3*lam + 2*mu) / (lam + mu)
            self.nu = lam / (2 * (lam + mu))
            self.lam = lam
            self.mu = mu
        elif e is not None and nu is not None:
            self.lam = nu * e / ((1 + nu) * (1 - 2 * nu))
            self.mu = e / (2 * (1 + nu))
            self.e = e
            self.nu = nu
        else:
            raise ValueError("Either (lam, mu) or (e, nu) should be provided.")
        self.elasticity_type = elasticity_type
        self.device = device
        self.coef = coef
        self.q = q
        self.index = index
        self.batched = batched

    @enable_cache
    def to_global_dof(self, space: _FS) -> Tensor:
        return space.cell_to_dof()[self.index]

    @enable_cache
    def fetch(self, space: _FS):
        q = self.q
        index = self.index
        mesh = getattr(space, 'mesh', None)
    
        if not isinstance(mesh, HomogeneousMesh):
            raise RuntimeError("The LinearElasticityIntegrator only support spaces on"
                               f"homogeneous meshes, but {type(mesh).__name__} is"
                               "not a subclass of HomoMesh.")
    
        cm = mesh.entity_measure('cell', index=index)
        qf = mesh.integrator(q, 'cell')
        bcs, ws = qf.get_quadrature_points_and_weights()
        gphi = space.grad_basis(bcs, index=index, variable='x')
        return bcs, ws, gphi, cm, index, q
    
    @enable_cache
    def elasticity_matrix(self, space: _FS):
        elasticity_type = self.elasticity_type
        scalar_space = space.scalar_space
        _, _, gphi, _, _, _ = self.fetch(scalar_space)
        _, GD = gphi.shape[-2:]

        if elasticity_type == 'stress':
            e, nu = self.e, self.nu
            if GD == 2:
                D = e / (1 - nu**2) *\
                    torch.tensor([[1, nu, 0],
                                  [nu, 1, 0],
                                  [0, 0, (1 - nu) / 2]], device=self.device, dtype=torch.float64)
            elif GD == 3:
                raise ValueError("Invalid GD dimension for stress.")
            else:
                raise ValueError("Invalid GD dimension.")
        elif elasticity_type == 'strain':
            mu, lam = self.mu, self.lam
            if GD == 2:
                D = torch.tensor([[2 * mu + lam, lam, 0],
                                  [lam, 2 * mu + lam, 0],
                                  [0, 0, mu]], device=self.device, dtype=torch.float64)
            elif GD == 3:
                D = torch.tensor([[2 * mu + lam, lam, lam, 0, 0, 0],
                                  [lam, 2 * mu + lam, lam, 0, 0, 0],
                                  [lam, lam, 2 * mu + lam, 0, 0, 0],
                                  [0, 0, 0, mu, 0, 0],
                                  [0, 0, 0, 0, mu, 0],
                                  [0, 0, 0, 0, 0, mu]], device=self.device, dtype=torch.float64)
            else:
                raise ValueError("Invalid GD dimension.")
        else:
            raise ValueError("Unknown type.")
        
        return D
    
    @enable_cache
    def strain_matrix(self, space: _FS):
        scalar_space = space.scalar_space
        _, _, gphi, _, _, _ = self.fetch(scalar_space)
        ldof, GD = gphi.shape[-2:]
        if space.dof_last:
            indices = flatten_indices((ldof, GD), (1, 0))
        else:
            indices = flatten_indices((ldof, GD), (0, 1))
        B = torch.cat([normal_strain(gphi, indices),
                       shear_strain(gphi, indices)], dim=-2)
        return B
    
    def assembly(self, space: _FS) -> Tensor:
        coef = self.coef
        scalar_space = space.scalar_space
        mesh = getattr(space, 'mesh', None)
        bcs, ws, _, cm, index, _ = self.fetch(scalar_space)
        coef = process_coef_func(coef, bcs=bcs, mesh=mesh, etype='cell', index=index)
        D = self.elasticity_matrix(space)
        B = self.strain_matrix(space)

        return trilinear_integral(B, D, B , ws, cm, coef, batched=self.batched)


    @assemblymethod('fast_strain')
    def fast_assembly_strain_constant(self, space: _FS) -> Tensor:
        pass

    @assemblymethod('fast_stress')
    def fast_assembly_stress_constant(self, space: _FS) -> Tensor:
        pass

    @assemblymethod('fast_3d')
    def fast_assembly_constant(self, space: _FS) -> Tensor:
        pass