import numpy as np
from typing import Callable, List, Tuple
from .curve_analysis import Vector3d, CurveAnalyzer


class RulingCalculator:
    """
    Compute ruling vectors for CCU (Curved-Crease Unfolding).
    DFS (Discrete Folding Symmetry) implementation.
    Equations (1)-(4) from paper.
    """

    def __init__(self, analyzer: CurveAnalyzer, ruling_angle_func: Callable = None):
        """
        analyzer: CurveAnalyzer instance
        ruling_angle_func: Callable γ(i) -> angle in radians
                          If None, uses default γ = π/2 (ultra-special case)
        """
        self.analyzer = analyzer
        if ruling_angle_func is None:
            ruling_angle_func = lambda i: np.pi / 2
        self.ruling_angle_func = ruling_angle_func

        self.ruling_vectors: List[Tuple[Vector3d, Vector3d]] = []
        self._compute_rulings_flat()

    def _compute_rulings_flat(self):
        """
        Compute ruling vectors in the 2D crease pattern (flat state, α=0).
        For each point i, compute R_left and R_right.
        """
        n = len(self.analyzer.points)

        for i in range(n):
            γ = self.ruling_angle_func(i)
            T = self.analyzer.tangents[i]
            N = self.analyzer.normals[i]
            B = self.analyzer.binormals[i]

            # In the flat state (α=0), ruling vectors are in the TN plane
            # R = cos(γ) * T + sin(γ) * N
            R = Vector3d(
                np.cos(γ) * T.x + np.sin(γ) * N.x,
                np.cos(γ) * T.y + np.sin(γ) * N.y,
                np.cos(γ) * T.z + np.sin(γ) * N.z,
            )

            # For CCU (unfolding): both left and right edges use the same ruling
            # This differs from CCF (folding) where they're opposite
            R_left = R
            R_right = R

            self.ruling_vectors.append((R_left, R_right))

    def get_rulings_at_deployment(self, alpha: float) -> List[Tuple[Vector3d, Vector3d]]:
        """
        Compute ruling vectors at deployment angle α.
        α=0: flat
        α=π/2: fully unfolded
        Uses Eq. from paper for CCU deployment.
        """
        deployed_rulings = []

        for i in range(len(self.analyzer.points)):
            γ = self.ruling_angle_func(i)
            T = self.analyzer.tangents[i]
            N = self.analyzer.normals[i]
            B = self.analyzer.binormals[i]

            # CCU ruling at deployment angle α:
            # R_left = cos(γ) * T + sin(γ) * cos(α) * N + sin(γ) * sin(α) * B
            # R_right = cos(γ) * T + sin(γ) * cos(α) * N - sin(γ) * sin(α) * B
            
            cos_gamma = np.cos(γ)
            sin_gamma = np.sin(γ)
            cos_alpha = np.cos(alpha)
            sin_alpha = np.sin(alpha)

            R_left = Vector3d(
                cos_gamma * T.x + sin_gamma * cos_alpha * N.x + sin_gamma * sin_alpha * B.x,
                cos_gamma * T.y + sin_gamma * cos_alpha * N.y + sin_gamma * sin_alpha * B.y,
                cos_gamma * T.z + sin_gamma * cos_alpha * N.z + sin_gamma * sin_alpha * B.z,
            )

            R_right = Vector3d(
                cos_gamma * T.x + sin_gamma * cos_alpha * N.x - sin_gamma * sin_alpha * B.x,
                cos_gamma * T.y + sin_gamma * cos_alpha * N.y - sin_gamma * sin_alpha * B.y,
                cos_gamma * T.z + sin_gamma * cos_alpha * N.z - sin_gamma * sin_alpha * B.z,
            )

            deployed_rulings.append((R_left, R_right))

        return deployed_rulings

    def get_ruling_at(self, index: int) -> Tuple[Vector3d, Vector3d]:
        """Get (R_left, R_right) at index in flat state"""
        return self.ruling_vectors[index]
