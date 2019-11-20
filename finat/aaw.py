import numpy

import FIAT

from gem import Literal, ListTensor

from finat.fiat_elements import FiatElement
from finat.physically_mapped import PhysicallyMappedElement, Citations


class ArnoldAwanouWinther(PhysicallyMappedElement, FiatElement):
    def __init__(self, cell, degree):
        super(ArnoldAwanouWinther, self).__init__(FIAT.ArnoldAwanouWinther(cell, degree))


    def basis_transformation(self, coordinate_mapping):
        V = numpy.zeros((18, 15), dtype=object)

        for multiindex in numpy.ndindex(V.shape):
            V[multiindex] = Literal(V[multiindex])

        for i in range(0, 12, 2):
            V[i, i] = Literal(1)

        T = self.cell

        # This bypasses the GEM wrapper.
        that = numpy.array([T.compute_normalized_edge_tangent(i) for i in range(3)])
        nhat = numpy.array([T.compute_normal(i) for i in range(3)])

        detJ = coordinate_mapping.detJ_at([1/3, 1/3])
        J = coordinate_mapping.jacobian_at([1/3, 1/3])
        J_np = numpy.array([[J[0, 0], J[0, 1]],
                            [J[1, 0], J[1, 1]]])
        JTJ = J_np.T @ J_np

        for e in range(3):
            
            # Compute alpha and beta for the edge.
            Ghat_T = numpy.array([nhat[e, :], that[e, :]])

            (alpha, beta) = Ghat_T @ JTJ @ that[e,:] / detJ

            # Stuff into the right rows and columns.
            (idx1, idx2) = (4*e + 1, 4*e + 3)
            V[idx1, idx1-1] = Literal(-1) * alpha / beta
            V[idx1, idx1] = Literal(1) / beta
            V[idx2, idx2-1] = Literal(-1) * alpha / beta
            V[idx2, idx2] = Literal(1) / beta

        # internal dofs
        for i in range(12, 15):
            V[i, i] = Literal(1)

        return ListTensor(V.T)


    def entity_dofs(self):
        return {0: {0: [],
                    1: [],
                    2: []},
                1: {0: [0, 1, 2, 3], 1: [4, 5, 6, 7], 2: [8, 9, 10, 11]},
                2: {0: [12, 13, 14]}}


    @property
    def index_shape(self):
        return (15,)


    def space_dimension(self):
        return 15
