import numpy as np
import matplotlib.pyplot as plt
import pytest

from fealpy.experimental.backend import backend_manager as bm
from fealpy.experimental.mesh.hexahedron_mesh import HexahedronMesh

from hexahedron_mesh_data import *

class TestHexahedronMeshInterfaces:
    @pytest.fixture(scope="class", params=backends)
    def backend(self, request):
        bm.set_backend(request.param)
        return request.param

    @pytest.mark.parametrize("bpdata", bc_to_point_data)
    def test_bc_to_point(self, bpdata, backend):
        mesh = HexahedronMesh.from_one_hexahedron(twist=True)

        bcs = bpdata["bcs"] 
        for i in range(len(bcs)):
            bcs[i] = bm.array(bcs[i])
        bcs = tuple(bcs)
        point_true = bpdata["point"]

        point = mesh.bc_to_point(bcs)
        np.testing.assert_allclose(bm.to_numpy(point), point_true, atol=1e-14)


    @pytest.mark.parametrize("jacobi_and_fff_data", jacobi_matrix_and_first_fundamental_form_data)
    def test_jacobi_matrix_and_first_fundamental_form(self, jacobi_and_fff_data, backend):
        mesh = HexahedronMesh.from_one_hexahedron(twist=True)

        bcs = jacobi_and_fff_data["bcs"]
        for i in range(len(bcs)):
            bcs[i] = bm.array(bcs[i])
        bcs = tuple(bcs)
        jacobi_true = jacobi_and_fff_data["jacobi"]
        fff_true = jacobi_and_fff_data["first_fundamental_form"]

        jacobi = mesh.jacobi_matrix(bcs)
        fff = mesh.first_fundamental_form(jacobi)

        np.testing.assert_allclose(bm.to_numpy(jacobi), jacobi_true, atol=1e-14)
        np.testing.assert_allclose(bm.to_numpy(fff), fff_true, atol=1e-14)

    @pytest.mark.parametrize("cipfip", cell_and_face_to_ipoint_data)
    def test_cell_and_face_to_ipoint(self, cipfip, backend):
        mesh = HexahedronMesh.from_one_hexahedron(twist=True)

        cip = mesh.cell_to_ipoint(2)
        fip = mesh.face_to_ipoint(2)

        cip_true = cipfip["cip"]
        fip_true = cipfip["fip"]

        np.testing.assert_allclose(bm.to_numpy(cip), cip_true, atol=1e-14)
        np.testing.assert_allclose(bm.to_numpy(fip), fip_true, atol=1e-14)

    @pytest.mark.parametrize("ip", interpolation_points_data)
    def test_interpolation_points(self, ip, backend):
        mesh = HexahedronMesh.from_one_hexahedron(twist=True)

        ip_true = ip["ip"]
        ip = mesh.interpolation_points(2)

        np.testing.assert_allclose(bm.to_numpy(ip), ip_true, atol=1e-14)

    @pytest.mark.parametrize("urdata",  uniform_refine_data)
    def test_uniform_refine(self, urdata, backend):
        mesh = HexahedronMesh.from_one_hexahedron(twist=True)
        mesh.uniform_refine(2)

        node = mesh.entity('node')
        cell = mesh.entity('cell')
        face2cell = mesh.face_to_cell()
        cell2edge = mesh.cell_to_edge()
        cell2face = mesh.cell_to_face()
        face2edge = mesh.face_to_edge()

        node_true = urdata["node"]
        cell_true = urdata["cell"]
        face2cell_true = urdata["face2cell"]
        cell2edge_true = urdata["cell2edge"]
        cell2face_true = urdata["cell2face"]
        face2edge_true = urdata["face2edge"]

        np.testing.assert_allclose(bm.to_numpy(node), node_true, atol=1e-14)
        np.testing.assert_allclose(bm.to_numpy(cell), cell_true, atol=1e-14)
        np.testing.assert_allclose(bm.to_numpy(face2cell), face2cell_true, atol=1e-14)
        np.testing.assert_allclose(bm.to_numpy(cell2edge), cell2edge_true, atol=1e-14)
        np.testing.assert_allclose(bm.to_numpy(cell2face), cell2face_true, atol=1e-14)
        np.testing.assert_allclose(bm.to_numpy(face2edge), face2edge_true, atol=1e-14)

    @pytest.mark.parametrize("emdata", entity_measure_data)
    def test_entity_measure(self, emdata, backend):
        mesh = HexahedronMesh.from_one_hexahedron(twist=True)

        cm = mesh.entity_measure('cell')
        fm = mesh.entity_measure('face')
        em = mesh.entity_measure('edge')

        cm_true = emdata["cell"]
        fm_true = emdata["face"]
        em_true = emdata["edge"]

        np.testing.assert_allclose(bm.to_numpy(cm), cm_true, atol=1e-14)
        np.testing.assert_allclose(bm.to_numpy(fm), fm_true, atol=1e-14)
        np.testing.assert_allclose(bm.to_numpy(em), em_true, atol=1e-14)





