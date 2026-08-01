import numpy as np
from typing import List
from .curve_analysis import Point3d, Vector3d


class Strip:
    """
    Represents a single developable strip (plate) with thickness.
    Handles centerline, edges, and offset curves (axis-shift approach).
    """

    def __init__(
        self,
        centerline_points: List[Point3d],
        ruling_vectors: List[tuple],
        width: float,
        thickness: float,
        axis_shift_mode: str = "center",
    ):
        """
        centerline_points: Points along crease
        ruling_vectors: (R_left, R_right) tuples
        width: Half-width of strip
        thickness: Plate thickness
        axis_shift_mode: 'center', 'intrados', or 'extrados'
        """
        self.centerline = centerline_points
        self.ruling_vectors = ruling_vectors
        self.width = width
        self.thickness = thickness
        self.axis_shift_mode = axis_shift_mode

        self.left_edge: List[Point3d] = []
        self.right_edge: List[Point3d] = []
        self.offset_left: List[Point3d] = []
        self.offset_right: List[Point3d] = []

        self._compute_edges()
        self._apply_axis_shift()

    def _compute_edges(self):
        """Compute edge points from centerline + ruling vectors"""
        for pt, (R_left, R_right) in zip(self.centerline, self.ruling_vectors):
            left = Point3d(
                pt.x + self.width * R_left.x,
                pt.y + self.width * R_left.y,
                pt.z + self.width * R_left.z,
            )
            right = Point3d(
                pt.x + self.width * R_right.x,
                pt.y + self.width * R_right.y,
                pt.z + self.width * R_right.z,
            )
            self.left_edge.append(left)
            self.right_edge.append(right)

    def _apply_axis_shift(self):
        """Apply thickness offset perpendicular to surface (Sec. 5.3)"""
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
