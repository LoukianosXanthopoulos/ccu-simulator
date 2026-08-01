import numpy as np
from typing import List, Callable
from .curve_analysis import CurveAnalyzer, Point3d, Vector3d
from .rulings import RulingCalculator
from .thickness import Strip
from .mesh_topology import MeshBuilder


class MultiCreaseVault:
    """
    Array of parallel planes with alternating synclastic/anticlastic creases.
    Implements Sec. 5.1-5.2 logic with variable width and ruling angles.
    
    KEY: Each crease has ALTERNATING ruling directions (ridge vs valley):
    Ridge (i even): +cos(γ)*T + sin(γ)*cos(α)*N + sin(γ)*sin(α)*B
    Valley (i odd): -cos(γ)*T - sin(γ)*cos(α)*N - sin(γ)*sin(α)*B
    """

    def __init__(
        self,
        analyzer: CurveAnalyzer,
        ruling_calc: RulingCalculator,
        num_creases: int,
        strip_width: float = None,
        strip_width_func: Callable = None,
        strip_thickness: float = 1.0,
        plane_distance: float = 10.0,
        alternating: bool = True,
        inclination_mode: str = "parallel",
    ):
        """
        analyzer: CurveAnalyzer instance
        ruling_calc: RulingCalculator instance
        num_creases: Number of crease planes
        strip_width: Constant half-width (used if strip_width_func is None)
        strip_width_func: Callable(s: float, i: int) -> float, variable width by arc-length s and crease index i
        strip_thickness: Plate thickness
        plane_distance: Distance between planes (offset direction = binormal)
        alternating: If True, alternate ruling signs for ridge/valley effect
        inclination_mode: 'parallel', 'inclined_axis', 'inclined_perpendicular'
        """
        self.analyzer = analyzer
        self.ruling_calc = ruling_calc
        self.num_creases = num_creases
        self.strip_width = strip_width if strip_width is not None else 5.0
        self.strip_width_func = strip_width_func
        self.strip_thickness = strip_thickness
        self.plane_distance = plane_distance
        self.alternating = alternating
        self.inclination_mode = inclination_mode

        self.strips: List[Strip] = []
        self.meshes: List[MeshBuilder] = []
        self.crease_rulings: List[List[tuple]] = []  # Rulings for each crease (modified by alternation)

        self._generate_vault()

    def _get_width_at(self, s: float, crease_index: int) -> float:
        """Get strip width at arc-length position s for crease crease_index"""
        if self.strip_width_func is not None:
            return self.strip_width_func(s, crease_index)
        return self.strip_width

    def _compute_alternating_rulings(self, crease_index: int) -> List[tuple]:
        """
        Compute ruling vectors for this crease with alternation.
        Ridge (even): standard rulings from ruling_calc
        Valley (odd): negated rulings
        """
        base_rulings = self.ruling_calc.ruling_vectors
        
        if not self.alternating:
            return base_rulings
        
        if crease_index % 2 == 0:
            # Ridge: use standard rulings
            return base_rulings
        else:
            # Valley: negate all rulings
            negated = [
                (
                    Vector3d(-R_left.x, -R_left.y, -R_left.z),
                    Vector3d(-R_right.x, -R_right.y, -R_right.z),
                )
                for R_left, R_right in base_rulings
            ]
            return negated

    def _generate_vault(self):
        """Generate multi-crease corrugated vault with alternating ridge/valley"""
        for i in range(self.num_creases):
            # Translate centerline by offset in binormal direction
            offset_dir = self.analyzer.binormals[0]  # Use first binormal as default
            offset_amount = i * self.plane_distance

            offset_pts = [
                Point3d(
                    pt.x + offset_amount * offset_dir.x,
                    pt.y + offset_amount * offset_dir.y,
                    pt.z + offset_amount * offset_dir.z,
                )
                for pt in self.analyzer.points
            ]

            # Get alternating rulings for this crease
            crease_rulings = self._compute_alternating_rulings(i)
            self.crease_rulings.append(crease_rulings)

            # Create strip with variable width if function provided
            if self.strip_width_func is not None:
                # Build width list per point
                widths = [self._get_width_at(self.analyzer.t_params[j], i) 
                         for j in range(len(self.analyzer.points))]
                strip = VariableWidthStrip(
                    offset_pts,
                    crease_rulings,
                    widths,
                    self.strip_thickness,
                )
            else:
                strip = Strip(
                    offset_pts,
                    crease_rulings,
                    self.strip_width,
                    self.strip_thickness,
                )
            self.strips.append(strip)

            # Create mesh
            mesh = MeshBuilder(offset_pts, crease_rulings, self.strip_width)
            self.meshes.append(mesh)

    def get_all_vertices_array(self) -> np.ndarray:
        """Collect all vertices from all meshes"""
        all_verts = []
        for mesh in self.meshes:
            all_verts.append(mesh.get_vertices_array())
        return np.vstack(all_verts) if all_verts else np.array([])

    def get_all_faces_array(self, offset_indices: bool = True) -> np.ndarray:
        """Collect all faces with optional vertex offset"""
        all_faces = []
        vertex_offset = 0
        for mesh in self.meshes:
            faces = mesh.get_faces_array()
            if offset_indices:
                faces = faces + vertex_offset
            all_faces.append(faces)
            vertex_offset += len(mesh.vertices)
        return np.vstack(all_faces) if all_faces else np.array([])

    def get_crease_at_index(self, crease_index: int) -> MeshBuilder:
        """Get mesh for crease i"""
        return self.meshes[crease_index]


class VariableWidthStrip:
    """
    Strip with per-point variable width.
    Width varies along the crease via width_list[j] at point j.
    """

    def __init__(
        self,
        centerline_points: List[Point3d],
        ruling_vectors: List[tuple],
        width_list: List[float],
        thickness: float,
    ):
        """
        centerline_points: Points along crease
        ruling_vectors: (R_left, R_right) tuples
        width_list: Width at each point (len == len(centerline_points))
        thickness: Plate thickness
        """
        if len(width_list) != len(centerline_points):
            raise ValueError(
                f"width_list length {len(width_list)} != centerline length {len(centerline_points)}"
            )

        self.centerline = centerline_points
        self.ruling_vectors = ruling_vectors
        self.width_list = width_list
        self.thickness = thickness

        self.left_edge: List[Point3d] = []
        self.right_edge: List[Point3d] = []
        self.offset_left: List[Point3d] = []
        self.offset_right: List[Point3d] = []

        self._compute_edges()
        self._apply_axis_shift()

    def _compute_edges(self):
        """Compute edge points using per-point variable width"""
        for j, (pt, (R_left, R_right), width) in enumerate(
            zip(self.centerline, self.ruling_vectors, self.width_list)
        ):
            left = Point3d(
                pt.x + width * R_left.x,
                pt.y + width * R_left.y,
                pt.z + width * R_left.z,
            )
            right = Point3d(
                pt.x + width * R_right.x,
                pt.y + width * R_right.y,
                pt.z + width * R_right.z,
            )
            self.left_edge.append(left)
            self.right_edge.append(right)

    def _apply_axis_shift(self):
        """Apply thickness offset perpendicular to surface"""
        offset_vec = Vector3d(0, 0, self.thickness / 2)

        for left_pt, right_pt in zip(self.left_edge, self.right_edge):
            self.offset_left.append(
                Point3d(
                    left_pt.x + offset_vec.x,
                    left_pt.y + offset_vec.y,
                    left_pt.z + offset_vec.z,
                )
            )
            self.offset_right.append(
                Point3d(
                    right_pt.x + offset_vec.x,
                    right_pt.y + offset_vec.y,
                    right_pt.z + offset_vec.z,
                )
            )
