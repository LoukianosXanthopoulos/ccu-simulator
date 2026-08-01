import numpy as np
from typing import List
from .curve_analysis import CurveAnalyzer, Point3d, Vector3d
from .rulings import RulingCalculator


class Deployment:
    """
    Simulate deployment from flat (α=0) to spatial configuration (α=α_target).
    Uses Eq. (8): κ_2D → κ_3D via trigonometric relations.
    
    For CCU, the crease curve evolves as:
    - At α=0 (flat): crease is 2D, curvature κ_2D
    - At α=π/2 (deployed): crease is 3D, curvature κ_3D
    
    The relationship is: cos(α) = κ_2D / κ_3D (Eq. 8)
    """

    def __init__(self, analyzer: CurveAnalyzer, ruling_calc: RulingCalculator):
        self.analyzer = analyzer
        self.ruling_calc = ruling_calc

    def deploy(self, alpha: float) -> List[Point3d]:
        """
        Redeploy centerline points based on deployment angle α.
        
        Simple version: For now, return points with ruling vectors rotated at α.
        Full version would solve the curvature evolution equation.
        """
        # Placeholder: return original centerline
        # In full implementation, would recompute crease curvature via Eq. (8)
        return self.analyzer.points

    def get_deployed_rulings(self, alpha: float):
        """Get ruling vectors at deployment angle α"""
        return self.ruling_calc.get_rulings_at_deployment(alpha)

    def compute_crease_curvature_at_deployment(self, alpha: float) -> List[float]:
        """
        Compute 3D crease curvature κ_3D at deployment angle α.
        From Eq. (8): κ_3D = κ_2D / cos(α)
        
        Returns list of curvatures at each point along crease.
        """
        if abs(np.cos(alpha)) < 1e-10:
            # Near singularity: α ≈ π/2
            return [float('inf')] * len(self.analyzer.curvatures)
        
        k_3d = [k_2d / np.cos(alpha) for k_2d in self.analyzer.curvatures]
        return k_3d
