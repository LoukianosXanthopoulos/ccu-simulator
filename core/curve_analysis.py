import numpy as np
from typing import Callable, List, Tuple
from dataclasses import dataclass


@dataclass
class Point3d:
    """Simple 3D point"""
    x: float
    y: float
    z: float

    def __add__(self, other):
        return Point3d(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Point3d(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar):
        return Point3d(self.x * scalar, self.y * scalar, self.z * scalar)

    def __rmul__(self, scalar):
        return self * scalar

    def to_array(self):
        return np.array([self.x, self.y, self.z])

    @staticmethod
    def from_array(arr):
        return Point3d(float(arr[0]), float(arr[1]), float(arr[2]))


@dataclass
class Vector3d:
    """Simple 3D vector"""
    x: float
    y: float
    z: float

    def __add__(self, other):
        return Vector3d(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector3d(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar):
        return Vector3d(self.x * scalar, self.y * scalar, self.z * scalar)

    def __rmul__(self, scalar):
        return self * scalar

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        return Vector3d(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def magnitude(self):
        return np.sqrt(self.x**2 + self.y**2 + self.z**2)

    def normalize(self):
        mag = self.magnitude()
        if mag < 1e-10:
            return Vector3d(0, 0, 0)
        return Vector3d(self.x / mag, self.y / mag, self.z / mag)

    def to_array(self):
        return np.array([self.x, self.y, self.z])

    @staticmethod
    def from_array(arr):
        return Vector3d(float(arr[0]), float(arr[1]), float(arr[2]))


class CurveAnalyzer:
    """
    Analyze a parametric curve: discretize, compute Frenet-Serret frame.
    Input: Callable C(t) -> Point3d, where t ∈ [0, 1]
    Output: Discrete points + T, N, B vectors at each point
    """

    def __init__(self, curve_func: Callable, resolution: int = 50):
        """
        curve_func: Callable taking t ∈ [0, 1] returning Point3d
        resolution: Number of discretization points
        """
        self.curve_func = curve_func
        self.resolution = resolution

        self.points: List[Point3d] = []
        self.tangents: List[Vector3d] = []
        self.normals: List[Vector3d] = []
        self.binormals: List[Vector3d] = []
        self.curvatures: List[float] = []
        self.t_params: List[float] = []

        self._discretize_and_analyze()

    def _discretize_and_analyze(self):
        """Discretize curve and compute Frenet frame at each point"""
        dt = 1.0 / (self.resolution - 1) if self.resolution > 1 else 1.0
        h = dt * 0.001  # Finite difference step for derivatives

        for i in range(self.resolution):
            t = i * dt
            self.t_params.append(t)

            # Evaluate curve at t, t-h, t+h
            pt = self.curve_func(t)
            pt_plus = self.curve_func(t + h)
            pt_minus = self.curve_func(t - h) if t > 0 else pt

            self.points.append(pt)

            # First derivative (tangent direction)
            dC_dt = Vector3d(
                (pt_plus.x - pt_minus.x) / (2 * h),
                (pt_plus.y - pt_minus.y) / (2 * h),
                (pt_plus.z - pt_minus.z) / (2 * h),
            )
            T = dC_dt.normalize()
            self.tangents.append(T)

            # Second derivative (for curvature & normal)
            pt_plus2 = self.curve_func(t + 2 * h)
            pt_minus2 = self.curve_func(t - 2 * h) if t > 0 else pt

            d2C_dt2 = Vector3d(
                (pt_plus2.x - 2 * pt.x + pt_minus2.x) / (4 * h**2),
                (pt_plus2.y - 2 * pt.y + pt_minus2.y) / (4 * h**2),
                (pt_plus2.z - 2 * pt.z + pt_minus2.z) / (4 * h**2),
            )

            # Curvature: κ = |T' × T''| / |T'|^3
            cross = dC_dt.cross(d2C_dt2)
            dC_mag = dC_dt.magnitude()
            if dC_mag > 1e-10:
                kappa = cross.magnitude() / (dC_mag**3)
            else:
                kappa = 0.0
            self.curvatures.append(kappa)

            # Normal: perpendicular to T in direction of curvature
            if kappa > 1e-8:
                N = (d2C_dt2 - (d2C_dt2.dot(T) * T)).normalize()
            else:
                N = self._perpendicular_to(T)

            if N.magnitude() < 1e-8:
                N = self._perpendicular_to(T)

            self.normals.append(N)

            # Binormal: B = T × N
            B = T.cross(N).normalize()
            self.binormals.append(B)

    @staticmethod
    def _perpendicular_to(v: Vector3d) -> Vector3d:
        """Return a unit vector perpendicular to v"""
        if abs(v.z) < 0.9:
            perp = Vector3d(0, 0, 1).cross(v).normalize()
        else:
            perp = Vector3d(1, 0, 0).cross(v).normalize()
        return perp if perp.magnitude() > 1e-8 else Vector3d(1, 0, 0)

    def get_frame_at(self, index: int) -> Tuple[Point3d, Vector3d, Vector3d, Vector3d]:
        """Get (point, T, N, B) at index"""
        return (
            self.points[index],
            self.tangents[index],
            self.normals[index],
            self.binormals[index],
        )

    def eval_at_t(self, t: float) -> Tuple[Point3d, Vector3d, Vector3d, Vector3d]:
        """Interpolate frame at arbitrary t ∈ [0, 1]"""
        # Simple linear interpolation
        idx_low = int(t * (self.resolution - 1))
        idx_high = min(idx_low + 1, self.resolution - 1)
        frac = (t * (self.resolution - 1)) - idx_low

        pt = self.points[idx_low] + (self.points[idx_high] - self.points[idx_low]) * frac
        T = self.tangents[idx_low] + (self.tangents[idx_high] - self.tangents[idx_low]) * frac
        N = self.normals[idx_low] + (self.normals[idx_high] - self.normals[idx_low]) * frac
        B = self.binormals[idx_low] + (self.binormals[idx_high] - self.binormals[idx_low]) * frac

        return (pt, T.normalize(), N.normalize(), B.normalize())
