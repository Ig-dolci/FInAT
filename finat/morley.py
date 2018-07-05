import numpy

import FIAT

from gem import Division, Indexed, Literal, ListTensor, Product, Sum

from finat.fiat_elements import ScalarFiatElement
from finat.physically_mapped import PhysicallyMappedElement, Citations


class Morley(PhysicallyMappedElement, ScalarFiatElement):
    def __init__(self, cell, degree):
        if degree != 2:
            raise ValueError("Degree must be 2 for Morley element")
        if Citations is not None:
            Citations().register("Morley1971")
        super().__init__(FIAT.Morley(cell))

    def basis_transformation(self, coordinate_mapping):
        # Jacobians at edge midpoints
        J = coordinate_mapping.jacobian_at([1/3, 1/3])

        rns = coordinate_mapping.reference_normals()
        pns = coordinate_mapping.physical_normals()

        pts = coordinate_mapping.physical_tangents()

        pel = coordinate_mapping.physical_edge_lengths()

        B11 = [Sum(Product(Indexed(rns, (i, 0)),
                           Sum(Product(Indexed(pns, (i, 0)),
                                       Indexed(J, (0, 0))),
                               Product(Indexed(pns, (i, 1)),
                                       Indexed(J, (1, 0))))),
                   Product(Indexed(rns, (i, 1)),
                           Sum(Product(Indexed(pns, (i, 0)),
                                       Indexed(J, (0, 1))),
                               Product(Indexed(pns, (i, 1)),
                                       Indexed(J, (1, 1))))))
               for i in range(3)]

        B12 = [Sum(Product(Indexed(rns, (i, 0)),
                           Sum(Product(Indexed(pts, (i, 0)),
                                       Indexed(J, (0, 0))),
                               Product(Indexed(pts, (i, 1)),
                                       Indexed(J, (1, 0))))),
                   Product(Indexed(rns, (i, 1)),
                           Sum(Product(Indexed(pts, (i, 0)),
                                       Indexed(J, (0, 1))),
                               Product(Indexed(pts, (i, 1)),
                                       Indexed(J, (1, 1))))))
               for i in range(3)]

        V = numpy.eye(6, dtype=object)
        for multiindex in numpy.ndindex(V.shape):
            V[multiindex] = Literal(V[multiindex])

        for i in range(3):
            V[i + 3, i + 3] = B11[i]

        for i, c in enumerate([(1, 2), (0, 2), (0, 1)]):
            V[3+i, c[0]] = Division(Product(Literal(-1), B12[i]), Indexed(pel, (i, )))
            V[3+i, c[1]] = Division(B12[i], Indexed(pel, (i, )))

        # diagonal post-scaling to patch up conditioning
        h = coordinate_mapping.cell_size()

        for j in range(3):
            for i in range(6):
                V[i, 3+j] = Division(V[i, 3+j], Indexed(h, (j,)))

        return ListTensor(V.T)