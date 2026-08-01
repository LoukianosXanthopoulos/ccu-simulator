import numpy as np
from typing import List, Tuple
import struct


class MeshExporter:
    """
    Export 3D mesh to OBJ and STL formats.
    Handles quad faces by triangulating them.
    """

    def __init__(self, vertices: np.ndarray, faces: np.ndarray):
        """
        vertices: Nx3 array of vertex coordinates
        faces: Mx4 array of quad face indices (will triangulate to triangles)
        """
        self.vertices = vertices
        self.faces = faces
        self.triangles = self._triangulate_quads()

    def _triangulate_quads(self) -> np.ndarray:
        """Convert quad faces to triangles (split along diagonal 0-2)"""
        triangles = []
        for quad in self.faces:
            # Quad: [0, 1, 2, 3] -> triangles [0,1,2] and [0,2,3]
            triangles.append([quad[0], quad[1], quad[2]])
            triangles.append([quad[0], quad[2], quad[3]])
        return np.array(triangles)

    def export_obj(self, filename: str = "mesh.obj"):
        """Export mesh to OBJ format"""
        with open(filename, "w") as f:
            f.write("# OBJ file exported from CCU simulator\n")
            f.write(f"# Vertices: {len(self.vertices)}\n")
            f.write(f"# Faces (triangulated): {len(self.triangles)}\n\n")

            # Write vertices
            for v in self.vertices:
                f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")

            f.write("\n")

            # Write faces (OBJ uses 1-based indexing)
            for tri in self.triangles:
                f.write(f"f {tri[0]+1} {tri[1]+1} {tri[2]+1}\n")

        print(f"✓ Mesh exported to OBJ: {filename}")

    def export_stl_ascii(self, filename: str = "mesh.stl"):
        """Export mesh to ASCII STL format"""
        with open(filename, "w") as f:
            f.write("solid CCU_Mesh\n")

            for tri in self.triangles:
                v0 = self.vertices[tri[0]]
                v1 = self.vertices[tri[1]]
                v2 = self.vertices[tri[2]]

                # Compute normal via cross product
                edge1 = v1 - v0
                edge2 = v2 - v0
                normal = np.cross(edge1, edge2)
                norm_len = np.linalg.norm(normal)
                if norm_len > 1e-10:
                    normal = normal / norm_len
                else:
                    normal = np.array([0, 0, 1])

                f.write(f"  facet normal {normal[0]:.6e} {normal[1]:.6e} {normal[2]:.6e}\n")
                f.write("    outer loop\n")
                f.write(f"      vertex {v0[0]:.6e} {v0[1]:.6e} {v0[2]:.6e}\n")
                f.write(f"      vertex {v1[0]:.6e} {v1[1]:.6e} {v1[2]:.6e}\n")
                f.write(f"      vertex {v2[0]:.6e} {v2[1]:.6e} {v2[2]:.6e}\n")
                f.write("    endloop\n")
                f.write("  endfacet\n")

            f.write("endsolid CCU_Mesh\n")

        print(f"✓ Mesh exported to ASCII STL: {filename}")

    def export_stl_binary(self, filename: str = "mesh.stl"):
        """Export mesh to binary STL format (more compact)"""
        with open(filename, "wb") as f:
            # 80-byte header
            header = b"CCU Simulator Mesh Export" + b"\0" * (80 - 24)
            f.write(header)

            # Number of triangles (uint32, little-endian)
            n_triangles = len(self.triangles)
            f.write(struct.pack("<I", n_triangles))

            # Write each triangle
            for tri in self.triangles:
                v0 = self.vertices[tri[0]]
                v1 = self.vertices[tri[1]]
                v2 = self.vertices[tri[2]]

                # Compute normal
                edge1 = v1 - v0
                edge2 = v2 - v0
                normal = np.cross(edge1, edge2)
                norm_len = np.linalg.norm(normal)
                if norm_len > 1e-10:
                    normal = normal / norm_len
                else:
                    normal = np.array([0, 0, 1])

                # Write normal (3 floats)
                f.write(struct.pack("<fff", normal[0], normal[1], normal[2]))

                # Write vertices (3 vertices × 3 floats each)
                f.write(struct.pack("<fff", v0[0], v0[1], v0[2]))
                f.write(struct.pack("<fff", v1[0], v1[1], v1[2]))
                f.write(struct.pack("<fff", v2[0], v2[1], v2[2]))

                # Attribute byte count (uint16, unused)
                f.write(struct.pack("<H", 0))

        print(f"✓ Mesh exported to binary STL: {filename}")


def export_mesh_multi_format(
    vertices: np.ndarray,
    faces: np.ndarray,
    basename: str = "mesh",
    formats: List[str] = ["obj", "stl_ascii", "stl_binary"],
):
    """
    Export mesh to multiple formats at once.
    formats: List of 'obj', 'stl_ascii', 'stl_binary'
    """
    exporter = MeshExporter(vertices, faces)

    if "obj" in formats:
        exporter.export_obj(f"{basename}.obj")
    if "stl_ascii" in formats:
        exporter.export_stl_ascii(f"{basename}_ascii.stl")
    if "stl_binary" in formats:
        exporter.export_stl_binary(f"{basename}_binary.stl")
