import numpy as np
from typing import List, Tuple
from .curve_analysis import Point3d, Vector3d


class MeshBuilder:
    """
    Build quad mesh topology from centerline + ruling vectors.
    Represents CCU strip as a collection of 4-vertex faces.
    """

    def __init__(
        self,
        centerline_points: List[Point3d],
        ruling_vectors: List[Tuple[Vector3d, Vector3d]],
        width: float,
    ):
        """
        centerline_points: Points along the crease (center curve)
        ruling_vectors: (R_left, R_right) at each point
        width: Half-width of strip (total width = 2*width)
        """
        self.centerline = centerline_points
        self.rulings = ruling_vectors
        self.width = width

        self.vertices: List[Point3d] = []
        self.faces: List[Tuple[int, int, int, int]] = []  # Quad face indices

        self._build_mesh()

    def _build_mesh(self):
        """Construct vertices and quad faces"""
        n = len(self.centerline)

        # Build three edge point lists
        left_edge = []
        right_edge = []

        for i in range(n):
            pt = self.centerline[i]
            R_left, R_right = self.rulings[i]

            # Compute edge points: centerline ± width * ruling
            left_pt = Point3d(
                pt.x + self.width * R_left.x,
                pt.y + self.width * R_left.y,
                pt.z + self.width * R_left.z,
            )
            right_pt = Point3d(
                pt.x + self.width * R_right.x,
                pt.y + self.width * R_right.y,
                pt.z + self.width * R_right.z,
            )

            left_edge.append(left_pt)
            right_edge.append(right_pt)

        # Assemble vertices: [centerline, left_edge, right_edge]
        self.vertices = self.centerline + left_edge + right_edge
        n_verts_per_edge = n

        # Build quad faces
        for i in range(n - 1):
            # Left half: centerline[i] -> centerline[i+1] -> left_edge[i+1] -> left_edge[i]
            v0 = i  # centerline[i]
            v1 = i + 1  # centerline[i+1]
            v2 = n_verts_per_edge + i + 1  # left_edge[i+1]
            v3 = n_verts_per_edge + i  # left_edge[i]
            self.faces.append((v0, v1, v2, v3))

            # Right half: centerline[i] -> right_edge[i] -> right_edge[i+1] -> centerline[i+1]
            v0 = i  # centerline[i]
            v1 = 2 * n_verts_per_edge + i  # right_edge[i]
            v2 = 2 * n_verts_per_edge + i + 1  # right_edge[i+1]
            v3 = i + 1  # centerline[i+1]
            self.faces.append((v0, v1, v2, v3))

    def get_vertices_array(self) -> np.ndarray:
        """Return Nx3 array of vertex coordinates"""
        return np.array([[v.x, v.y, v.z] for v in self.vertices])

    def get_faces_array(self) -> np.ndarray:
        """Return Mx4 array of quad face indices"""
        return np.array(self.faces)

    def export_obj_data(self) -> Tuple[List[str], List[str]]:
        """Export as OBJ format lines (vertices and faces)"""
        vertex_lines = [f"v {v.x} {v.y} {v.z}" for v in self.vertices]
        face_lines = [f"f {f[0]+1} {f[1]+1} {f[2]+1} {f[3]+1}" for f in self.faces]
        return vertex_lines, face_lines
