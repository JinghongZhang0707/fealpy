"""
外齿轮 15 个载荷点的算例
"""
from fealpy.backend import backend_manager as bm
from fealpy.mesh import HexahedronMesh
from fealpy.functionspace import LagrangeFESpace, TensorFunctionSpace
from fealpy.sparse import COOTensor
from fealpy.fem.linear_elastic_integrator import LinearElasticIntegrator
from fealpy.material.elastic_material import LinearElasticMaterial
from fealpy.fem.bilinear_form import BilinearForm
from fealpy.fem.dirichlet_bc import DirichletBC
from fealpy.solver import cg, spsolve

from app.soptx.linear_elasticity.JingYiGearProject.utils import export_to_inp

import pickle

def compute_strain_stress_1(space, uh, mu, lam):
    """在积分点处计算应变和应力"""
    mesh = space.mesh
    cell = mesh.entity('cell')
    cell2dof = space.cell_to_dof()
    NC = mesh.number_of_cells()

    # 计算积分点处的基函数梯度
    qf2 = mesh.quadrature_formula(2)
    bcs_q2, ws = qf2.get_quadrature_points_and_weights()
    gphix_q2 = space.grad_basis(bcs_q2, variable='x')  # (NC, NQ, LDOF, GD)

    cuh = uh[cell2dof]  # (NC, LDOF, GD)

    # 计算应变
    NQ = len(ws)  # 积分点个数
    strain = bm.zeros((NC, NQ, 6), dtype=bm.float64)
    
    # 计算正应变和剪切应变
    strain[:, :, 0:3] = bm.einsum('cid, cqid -> cqd', cuh, gphix_q2)  # (NC, NQ, 3)
    for i in range(NQ):  
        # strain[:, i, 3] = bm.sum(
        #         cuh[:, :, 2]*gphix_q2[:, i, :, 1] + cuh[:, :, 1]*gphix_q2[:, i, :, 2], 
        #         axis=-1) / 2.0  # (NC,)

        # strain[:, i, 4] = bm.sum(
        #         cuh[:, :, 2]*gphix_q2[:, i, :, 0] + cuh[:, :, 0]*gphix_q2[:, i, :, 2], 
        #         axis=-1) / 2.0  # (NC,)

        # strain[:, i, 5] = bm.sum(
        #         cuh[:, :, 1]*gphix_q2[:, i, :, 0] + cuh[:, :, 0]*gphix_q2[:, i, :, 1], 
        #         axis=-1) / 2.0  # (NC,)
        strain[:, i, 3] = bm.sum(
                cuh[..., 1]*gphix_q2[:, i, :, 0] + cuh[..., 0]*gphix_q2[:, i, :, 1], axis=-1)  # (NC,)
        strain[:, i, 4] = bm.sum(
                cuh[..., 2]*gphix_q2[:, i, :, 1] + cuh[..., 1]*gphix_q2[:, i, :, 2], axis=-1)  # (NC,)
        strain[:, i, 5] = bm.sum(
                cuh[..., 2]*gphix_q2[:, i, :, 0] + cuh[..., 0]*gphix_q2[:, i, :, 2], axis=-1)  # (NC,)

    # 计算应力
    val = 2*mu + lam
    stress = bm.zeros((NC, NQ, 6), dtype=bm.float64)
    stress[:, :, 0] = val * strain[:, :, 0] + lam * (strain[:, :, 1] + strain[:, :, 2])
    stress[:, :, 1] = val * strain[:, :, 1] + lam * (strain[:, :, 2] + strain[:, :, 0])
    stress[:, :, 2] = val * strain[:, :, 2] + lam * (strain[:, :, 0] + strain[:, :, 1])
    # stress[:, :, 3] = 2*mu * strain[:, :, 3]
    # stress[:, :, 4] = 2*mu * strain[:, :, 4]
    # stress[:, :, 5] = 2*mu * strain[:, :, 5]
    stress[:, :, 3] = mu * strain[:, :, 3]
    stress[:, :, 4] = mu * strain[:, :, 4]
    stress[:, :, 5] = mu * strain[:, :, 5]

    return strain, stress

def compute_strain_stress_2(tensor_space, uh, B, D):
    cell2tdof = tensor_space.cell_to_dof()
    cuh = uh[cell2tdof]  # (NC, TLDOF) 
    strain = bm.einsum('cqil, cl -> cqi', B, cuh) # (NC, NQ, 6)
    stress = bm.einsum('cqij, cqi -> cqj', D, strain) # (NC, NQ, 6)
    
    return strain, stress

def compute_strain_stress_3(tensor_space, uh, B_BBar, D):
    cell2tdof = tensor_space.cell_to_dof()
    cuh = uh[cell2tdof]  # (NC, TLDOF) 
    strain = bm.einsum('cqil, cl -> cqi', B_BBar, cuh) # (NC, NQ, 6)
    stress = bm.einsum('cqij, cqi -> cqj', D, strain) # (NC, NQ, 6)
    
    return strain, stress


bm.set_backend('numpy')

with open('/home/heliang/FEALPy_Development/fealpy/app/soptx/linear_elasticity/JingYiGearProject/pkl/external_gear.pkl', 'rb') as f:
    data = pickle.load(f)

external_gear = data['external_gear']
hex_mesh = data['hex_mesh']
# helix_node = data['helix_node']
is_inner_node = data['is_inner_node']

hex_cell = hex_mesh.cell
hex_node = hex_mesh.node
mesh = HexahedronMesh(hex_node, hex_cell)

GD = mesh.geo_dimension()   
NC = mesh.number_of_cells()
print(f"NC: {NC}")
NN = mesh.number_of_nodes()
print(f"NN: {NN}")
node = mesh.entity('node')
cell = mesh.entity('cell')

# 节点载荷
load_values = 100 * bm.array([50.0, 60.0, 79.0, 78.0, 87.0, 95.0, 102.0, 109.0, 114.0,
                        119.0, 123.0, 127.0, 129.0, 130.0, 131.0], dtype=bm.float64)   # (15, )

n = 15
helix_d = bm.linspace(external_gear.d, external_gear.effective_da, n)
helix_width = bm.linspace(0, external_gear.tooth_width, n)
helix_node = external_gear.cylindrical_to_cartesian(helix_d, helix_width)

target_cell_idx = bm.zeros(n, bm.int32)
face_normal = bm.zeros((n, 3), bm.float64)
parameters = bm.zeros((n, 3), bm.float64)
for i, t_node in enumerate(helix_node):
    target_cell_idx[i], face_normal[i], parameters[i] = external_gear.find_node_location_kd_tree(t_node)

average_normal = bm.mean(face_normal, axis=0)
average_normal /= bm.linalg.norm(average_normal)

threshold = 0.1
for i in range(len(face_normal)):
    deviation = bm.linalg.norm(face_normal[i] - average_normal)
    if deviation > threshold:
        face_normal[i] = average_normal

P = bm.einsum('p, pd -> pd', load_values, face_normal)  # (15, GD)

u = parameters[..., 0]
v = parameters[..., 1]
w = parameters[..., 2]

bcs_list = [
    (
        bm.tensor([[u, 1 - u]]),
        bm.tensor([[v, 1 - v]]),
        bm.tensor([[w, 1 - w]])
    )
    for u, v, w in zip(u, v, w)
]

# 创建有限元空间
p = 1
q = 2
space = LagrangeFESpace(mesh, p=p, ctype='C')
scalar_gdof = space.number_of_global_dofs()
print(f"gdof: {scalar_gdof}")
cell2dof = space.cell_to_dof()
tensor_space = TensorFunctionSpace(space, shape=(-1, 3)) # gd_priority
cell2tdof = tensor_space.cell_to_dof()
map = [ 0,  1,  2, 12, 13, 14,  9, 10, 11, 21, 22, 23,  3,  4,  5, 15, 16,
       17,  6,  7,  8, 18, 19, 20]
tgdof = tensor_space.number_of_global_dofs()
print(f"tgdof: {tgdof}")
tldof = tensor_space.number_of_local_dofs()

# 节点载荷的索引（去重）
load_node_indices0 = cell[target_cell_idx].flatten() # (15*8, )
unique_nodes, first_indices = bm.unique(load_node_indices0, return_index=True)
sort1_indices = bm.sort(first_indices)
load_node_indices = load_node_indices0[sort1_indices] # (15*8, )
# 带有载荷的节点对应的全局自由度编号（跟顺序有关）
if tensor_space.dof_priority:
    dof_indices = bm.stack([scalar_gdof * d + load_node_indices for d in range(GD)], axis=1)  # (15*8, GD)
else:
    dof_indices = bm.stack([load_node_indices * GD + d for d in range(GD)], axis=1)  # (15*8, GD)


phi_loads = []
for bcs in bcs_list:
    phi = tensor_space.basis(bcs)
    phi_loads.append(phi)

phi_loads_array = bm.concatenate(phi_loads, axis=1) # (1, 15, tldof, GD)

FE_load = bm.einsum('pd, cpld -> pl', P, phi_loads_array) # (15, 24)

FE = bm.zeros((NC, tldof), dtype=bm.float64)
FE[target_cell_idx, :] = FE_load[:, :] # (NC, tldof)

F = COOTensor(indices = bm.empty((1, 0), dtype=bm.int32, device=bm.get_device(space)),
            values = bm.empty((0, ), dtype=bm.float64, device=bm.get_device(space)),
            spshape = (tgdof, ))
indices = cell2tdof.reshape(1, -1)
F = F.add(COOTensor(indices, FE.reshape(-1), (tgdof, ))).to_dense() # (tgdof, )
non_zero_indices = bm.nonzero(F)[0]
non_zero_values = F[non_zero_indices]
F_non_zero = bm.concatenate([non_zero_indices[:, None], non_zero_values[:, None]], axis=1)
# np.savetxt('/home/heliang/FEALPy_Development/fealpy/app/soptx/linear_elasticity/txt/F_without_dc.csv', 
#            F, delimiter=',', fmt='%s')
# np.savetxt('/home/heliang/FEALPy_Development/fealpy/app/soptx/linear_elasticity/txt/F_non_zero_without_dc.csv', 
#            F_non_zero, delimiter='', fmt=['%10d', '%20.6f'])


# 从全局载荷向量中提取有载荷节点处的值
F_load_nodes = F[dof_indices] # (15*8, GD)

fixed_node_index = bm.where(is_inner_node)[0]
export_to_inp(filename='/home/heliang/FEALPy_Development/fealpy/app/soptx/linear_elasticity/JingYiGearProject/inp/external_gear_abaqus.inp', 
              nodes=node, elements=cell, 
              fixed_nodes=fixed_node_index, load_nodes=load_node_indices, loads=F_load_nodes, 
              young_modulus=206e3, poisson_ratio=0.3, density=7.85e-9, 
              used_app='abaqus', mesh_type='hex')

E = 206e3
nu = 0.3
lam = (E * nu) / ((1.0 + nu) * (1.0 - 2.0 * nu))
mu = E / (2.0 * (1.0 + nu))
linear_elastic_material = LinearElasticMaterial(name='E_nu', 
                                                elastic_modulus=E, poisson_ratio=nu, 
                                                hypo='3D', device=bm.get_device(mesh))

# B-Bar 修正的刚度矩阵
# integrator_K0 = LinearElasticIntegrator(material=linear_elastic_material, 
#                                         q=q, method='voigt')
# integrator_K0.keep_data(True)
# _, _, _, D, B = integrator_K0.fetch_voigt_assembly(tensor_space)
integrator_K = LinearElasticIntegrator(material=linear_elastic_material, 
                                       q=q, method='C3D8_BBar')
integrator_K.keep_data(True)
_, _, D, B_BBar = integrator_K.fetch_c3d8_bbar_assembly(tensor_space)
B_BBar0 = B_BBar[1000][3].round(6)
bform = BilinearForm(tensor_space)
bform.add_integrator(integrator_K)
K = bform.assembly(format='csr')


# 处理 Dirichlet 边界条件
scalar_is_bd_dof = bm.zeros(scalar_gdof, dtype=bm.bool)
scalar_is_bd_dof[:NN] = is_inner_node
tensor_is_bd_dof = tensor_space.is_boundary_dof(
                                threshold=(scalar_is_bd_dof, scalar_is_bd_dof, scalar_is_bd_dof), 
                                method='interp')
dbc = DirichletBC(space=tensor_space, 
                    gd=bm.zeros(tgdof), 
                    threshold=tensor_is_bd_dof, 
                    method='interp')
K, F = dbc.apply(K, F)

from fealpy import logger
logger.setLevel('INFO')
uh = tensor_space.function()
# uh[:] = cg(K, F, maxiter=10000, atol=1e-8, rtol=1e-8)
uh[:] = spsolve(K, F, solver="mumps")

# 计算残差向量和范数
residual = K.matmul(uh[:]) - F  
residual_norm = bm.sqrt(bm.sum(residual * residual))
print(f"Final residual norm: {residual_norm:.6e}")

if tensor_space.dof_priority:
    uh_show = uh.reshape(GD, NN).T
else:
    uh_show = uh.reshape(NN, GD)

uh_x = uh_show[:, 0]
uh_y = uh_show[:, 1]
uh_z = uh_show[:, 2]

uh_magnitude = bm.linalg.norm(uh_show, axis=1)

mesh.nodedata['uh'] = uh_show[:]
mesh.nodedata['uh_magnitude'] = uh_magnitude[:]

# NOTE 计算单元积分点处的应变和应力
strain3, stress3 = compute_strain_stress_3(tensor_space, uh, B_BBar, D) # (NC, NQ, 6)

extrapolation_matrix = bm.tensor([
            [-0.0490381057,  0.1830127019,  0.1830127019, -0.6830127019,  0.1830127019, -0.6830127019, -0.6830127019,  2.5490381057],
            [ 0.1830127019, -0.0490381057, -0.6830127019,  0.1830127019, -0.6830127019,  0.1830127019,  2.5490381057, -0.6830127019],
            [ 0.1830127019, -0.6830127019, -0.0490381057,  0.1830127019, -0.6830127019,  2.5490381057,  0.1830127019, -0.6830127019],
            [-0.6830127019,  0.1830127019,  0.1830127019, -0.0490381057,  2.5490381057, -0.6830127019, -0.6830127019,  0.1830127019],
            [ 0.1830127019, -0.6830127019, -0.6830127019,  2.5490381057, -0.0490381057,  0.1830127019,  0.1830127019, -0.6830127019],
            [-0.6830127019,  0.1830127019,  2.5490381057, -0.6830127019,  0.1830127019, -0.0490381057, -0.6830127019,  0.1830127019],
            [-0.6830127019,  2.5490381057,  0.1830127019, -0.6830127019,  0.1830127019, -0.6830127019, -0.0490381057,  0.1830127019],
            [ 2.5490381057, -0.6830127019, -0.6830127019,  0.1830127019, -0.6830127019,  0.1830127019,  0.1830127019, -0.0490381057]
            ], dtype=bm.float64) # (NQ, 8)

# 计算外插后的单元节点应变和应力
cell2dof_map = [0, 4, 6, 2, 1, 5, 7, 3]
extrapolation_map = [7, 3, 1, 5, 6, 2, 0, 4 ]
strain3_extrapolation = bm.einsum('lq, cqj -> clj', extrapolation_matrix, strain3)
stress3_extrapolation = bm.einsum('lq, cqj -> clj', extrapolation_matrix, stress3)

# 计算节点应变和应力
cell2dof_maps = cell2dof[:, cell2dof_map]
strain3_extrapolation_maps = strain3_extrapolation[:, extrapolation_map, :]
stress3_extrapolation_maps = stress3_extrapolation[:, extrapolation_map, :]

# 使用直接平均法计算节点应变和应力 
nstrain = bm.zeros((NN, 6), dtype=bm.float64)
nstress = bm.zeros((NN, 6), dtype=bm.float64)
nc = bm.zeros(NN, dtype=bm.int32)
bm.add_at(nc, cell2dof_maps, 1)
for i in range(6):
    bm.add_at(nstrain[:, i], cell2dof_maps.flatten(), strain3_extrapolation_maps[:, :, i].flatten())
    nstrain[:, i] /= nc
    bm.add_at(nstress[:, i], cell2dof_maps.flatten(), stress3_extrapolation_maps[:, :, i].flatten())
    nstress[:, i] /= nc

mesh.nodedata['nstrain'] = nstrain
mesh.nodedata['nstress'] = nstress

# ------------------------------------------------------------------------------
# 计算 Mises 应力（Von Mises Stress）
# ------------------------------------------------------------------------------
# 计算单元节点处的 Mises 应力
# 1. 获取外插后的单元节点处的应力分量
sigma_xx_node = stress3_extrapolation[..., 0]
sigma_yy_node = stress3_extrapolation[..., 1]
sigma_zz_node = stress3_extrapolation[..., 2]
tau_xy_node = stress3_extrapolation[..., 3]
tau_xz_node = stress3_extrapolation[..., 4]
tau_yz_node = stress3_extrapolation[..., 5]
# 2. 计算单元节点处的 Mises 应力
mises_elem_node = bm.sqrt(0.5 * (
                    (sigma_xx_node - sigma_yy_node)**2 +
                    (sigma_xx_node - sigma_zz_node)**2 +
                    (sigma_yy_node - sigma_zz_node)**2 +
                    6 * (tau_xy_node**2 + tau_xz_node**2 + tau_yz_node**2)
                )) # (NC, NCN)
mises_elem_node_map = [7, 3, 1, 5, 6, 2, 0, 4]
print(f"mises_node_0: {cell2dof[0][cell2dof_map]}\n, {mises_elem_node[0][mises_elem_node_map]}")
print(f"mises_node_1: {cell2dof[1][cell2dof_map]}\n, {mises_elem_node[1][mises_elem_node_map]}")
print(f"mises_node_1363: {cell2dof[1363][cell2dof_map]}\n, {mises_elem_node[1363][mises_elem_node_map]}")
print(f"mises_node_1364: {cell2dof[1364][cell2dof_map]}\n, {mises_elem_node[1364][mises_elem_node_map]}")
# 3. 平均分配到节点
mises_node = bm.zeros(NN, dtype=bm.float64)
nc = bm.zeros(NN, dtype=bm.int32)
bm.add_at(nc, cell2dof_maps, 1)
bm.add_at(mises_node, cell2dof_maps.flatten(), mises_elem_node[:, mises_elem_node_map].flatten())
mises_node /= nc

# 将 Voigt 表示法的应变转换为对称的 3x3 应变张量
# strain_tensors = bm.zeros((NN, 3, 3), dtype=bm.float64)
# strain_tensors[:, 0, 0] = nstrain[:, 0]  # ε_xx
# strain_tensors[:, 1, 1] = nstrain[:, 1]  # ε_yy
# strain_tensors[:, 2, 2] = nstrain[:, 2]  # ε_zz
# strain_tensors[:, 0, 1] = nstrain[:, 3] / 2  # γ_xy / 2
# strain_tensors[:, 1, 0] = nstrain[:, 3] / 2  # γ_xy / 2
# strain_tensors[:, 0, 2] = nstrain[:, 4] / 2  # γ_xz / 2
# strain_tensors[:, 2, 0] = nstrain[:, 4] / 2  # γ_xz / 2
# strain_tensors[:, 1, 2] = nstrain[:, 5] / 2  # γ_yz / 2
# strain_tensors[:, 2, 1] = nstrain[:, 5] / 2  # γ_yz / 2

# # 计算主应变
# principal_strains, _ = bm.linalg.eigh(strain_tensors) # (NN, 3)

# # 计算最大值主应变、最大绝对值主应变
# max_principal_strains = bm.max(principal_strains, axis=1) # (NN, )
# max_p0_p1 = bm.where(bm.abs(principal_strains[:, 0]) >= bm.abs(principal_strains[:, 1]),
#                     principal_strains[:, 0], principal_strains[:, 1])
# max_abs_principal_strains = bm.where(bm.abs(max_p0_p1) >= bm.abs(principal_strains[:, 2]),
#                                    max_p0_p1, principal_strains[:, 2])
# # idx_max_abs_strains = bm.argmax(bm.abs(principal_strains), axis=1)  # (NN,)
# # max_abs_principal_strains = principal_strains[:, idx_max_abs_strains]
# print(f"principal_strains28716: {principal_strains[28716]}")
# print(f"principal_strains33112: {principal_strains[33112]}")
# print(f"principal_strains30501: {principal_strains[30501]}")
# print(f"principal_strains30509: {principal_strains[30509]}")
# print(f"max_principal_strains28716: {max_principal_strains[28716]}") 
# print(f"max_principal_strains33112: {max_principal_strains[33112]}")   
# print(f"max_abs_principal_strains30501: {max_abs_principal_strains[30501]}")
# print(f"max_abs_principal_strains30509: {max_abs_principal_strains[30509]}")

# # 将 Voigt 表示法的应力转换为对称的 3x3 应力张量
# stress_tensors = bm.zeros((NN, 3, 3), dtype=bm.float64)
# stress_tensors[:, 0, 0] = nstress[:, 0]  # σ_xx
# stress_tensors[:, 1, 1] = nstress[:, 1]  # σ_yy
# stress_tensors[:, 2, 2] = nstress[:, 2]  # σ_zz
# stress_tensors[:, 0, 1] = nstress[:, 3]  # σ_xy
# stress_tensors[:, 1, 0] = nstress[:, 3]  # σ_xy
# stress_tensors[:, 0, 2] = nstress[:, 4]  # σ_xz
# stress_tensors[:, 2, 0] = nstress[:, 4]  # σ_xz
# stress_tensors[:, 1, 2] = nstress[:, 5]  # σ_yz
# stress_tensors[:, 2, 1] = nstress[:, 5]  # σ_yz

# # 计算主应力
# principal_stresses, _ = bm.linalg.eigh(stress_tensors) # (NN, 3)

# # 计算最大值主应力、最大绝对值主应力
# max_principal_stresses = bm.max(principal_stresses, axis=1) # (NN, )
# max_s0_s1 = bm.where(bm.abs(principal_stresses[:, 0]) >= bm.abs(principal_stresses[:, 1]),
#                     principal_stresses[:, 0], principal_stresses[:, 1])
# max_abs_principal_stresses = bm.where(bm.abs(max_s0_s1) >= bm.abs(principal_stresses[:, 2]),
#                                     max_s0_s1, principal_stresses[:, 2])
# idx_max_abs_stresses = bm.argmax(bm.abs(principal_stresses), axis=1)  # (NN,)
# max_abs_principal_stresses = principal_stresses[:, idx_max_abs_stresses]


# print(f"pricipal_stresses28716: {principal_stresses[28716]}")
# print(f"pricipal_stresses33112: {principal_stresses[33112]}")
# print(f"pricipal_stresses30501: {principal_stresses[30501]}")
# print(f"pricipal_stresses30509: {principal_stresses[30509]}")
# print(f"pricipal_stresses32679: {principal_stresses[32679]}")
# print(f"max_principal_stresss28716: {max_principal_stresses[28716]}") 
# print(f"max_principal_stresss33112: {max_principal_stresses[33112]}")
# print(f"max_principal_stresses30501: {max_principal_stresses[30501]}")
# print(f"max_principal_stresses30509: {max_principal_stresses[30509]}")
# print(f"max_principal_stresses32679: {max_principal_stresses[32679]}")
# print(f"max_abs_principal_stresses28716: {max_abs_principal_stresses[28716]}")
# print(f"max_abs_principal_stresses33112: {max_abs_principal_stresses[33112]}")   
# print(f"max_abs_principal_stresses30501: {max_abs_principal_stresses[30501]}")
# print(f"max_abs_principal_stresses30509: {max_abs_principal_stresses[30509]}")
# print(f"max_abs_principal_stresses32679: {max_abs_principal_stresses[32679]}")

# max_principal_stresses_max = bm.max(max_principal_stresses)
# max_principal_stresses_max_index = bm.argmax(max_principal_stresses)
# print(f"max_principal_stresses_max: {max_principal_stresses_max}")
# print(f"max_principal_stresses_max_index: {max_principal_stresses_max_index}")
# max_abs_principal_stresses_max = bm.max(max_abs_principal_stresses)
# max_abs_principal_stresses_max_index = bm.argmax(max_abs_principal_stresses)
# print(f"max_abs_principal_stresses_max: {max_abs_principal_stresses_max}")
# print(f"max_abs_principal_stresses_max_index: {max_abs_principal_stresses_max_index}")

mesh.nodedata['mises'] = mises_node
# mesh.nodedata['max_principal_strains'] = max_principal_strains
# mesh.nodedata['max_principal_stresses'] = max_principal_stresses
# mesh.nodedata['max_abs_principal_strains'] = max_abs_principal_strains
# mesh.nodedata['max_abs_principal_stresses'] = max_abs_principal_stresses
mesh.to_vtk('/home/heliang/FEALPy_Development/fealpy/app/soptx/linear_elasticity/JingYiGearProject/vtu/external_gear_fealpy.vtu')
print("-----------")