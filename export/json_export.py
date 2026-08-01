import json
import numpy as np
from typing import Dict, Any, List, Callable
from datetime import datetime


class CCUProjectSerializer:
    """
    Serialize and deserialize CCU simulator state to/from JSON.
    Enables reproducible designs and data sharing.
    """

    @staticmethod
    def serialize_project(
        project_name: str,
        curve_analyzer,
        ruling_calculator,
        multi_crease_vault,
        deployment_angle: float = 0.0,
        metadata: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Serialize entire CCU project to JSON-compatible dict.
        """
        if metadata is None:
            metadata = {}

        project = {
            "project_name": project_name,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata,
            "curve": CCUProjectSerializer._serialize_curve(curve_analyzer),
            "rulings": CCUProjectSerializer._serialize_rulings(ruling_calculator),
            "vault": CCUProjectSerializer._serialize_vault(multi_crease_vault),
            "deployment_angle": float(deployment_angle),
        }

        return project

    @staticmethod
    def _serialize_curve(analyzer) -> Dict[str, Any]:
        """Serialize curve analysis data"""
        return {
            "num_points": len(analyzer.points),
            "points": [
                {"x": float(pt.x), "y": float(pt.y), "z": float(pt.z)}
                for pt in analyzer.points
            ],
            "tangents": [
                {"x": float(t.x), "y": float(t.y), "z": float(t.z)}
                for t in analyzer.tangents
            ],
            "normals": [
                {"x": float(n.x), "y": float(n.y), "z": float(n.z)}
                for n in analyzer.normals
            ],
            "binormals": [
                {"x": float(b.x), "y": float(b.y), "z": float(b.z)}
                for b in analyzer.binormals
            ],
            "curvatures": [float(k) for k in analyzer.curvatures],
            "torsions": [float(t) for t in analyzer.torsions],
            "arc_length_params": [float(t) for t in analyzer.t_params],
        }

    @staticmethod
    def _serialize_rulings(ruling_calc) -> Dict[str, Any]:
        """Serialize ruling vectors"""
        return {
            "num_rulings": len(ruling_calc.ruling_vectors),
            "ruling_pairs": [
                {
                    "left": {"x": float(R_left.x), "y": float(R_left.y), "z": float(R_left.z)},
                    "right": {"x": float(R_right.x), "y": float(R_right.y), "z": float(R_right.z)},
                }
                for R_left, R_right in ruling_calc.ruling_vectors
            ],
        }

    @staticmethod
    def _serialize_vault(vault) -> Dict[str, Any]:
        """Serialize multi-crease vault topology"""
        vault_data = {
            "num_creases": vault.num_creases,
            "strip_width": float(vault.strip_width),
            "strip_thickness": float(vault.strip_thickness),
            "plane_distance": float(vault.plane_distance),
            "alternating": vault.alternating,
            "inclination_mode": vault.inclination_mode,
            "creases": [],
        }

        for i, mesh in enumerate(vault.meshes):
            crease_data = {
                "crease_index": i,
                "num_vertices": len(mesh.vertices),
                "num_faces": len(mesh.faces),
                "vertices": [
                    {"x": float(v.x), "y": float(v.y), "z": float(v.z)}
                    for v in mesh.vertices
                ],
                "faces": [
                    [int(f[0]), int(f[1]), int(f[2]), int(f[3])]
                    for f in mesh.faces
                ],
            }
            vault_data["creases"].append(crease_data)

        return vault_data

    @staticmethod
    def save_project_to_file(
        project_dict: Dict[str, Any],
        filename: str = "ccu_project.json",
    ):
        """Save serialized project to JSON file"""
        with open(filename, "w") as f:
            json.dump(project_dict, f, indent=2)
        print(f"✓ Project saved to {filename}")

    @staticmethod
    def load_project_from_file(filename: str) -> Dict[str, Any]:
        """Load project from JSON file"""
        with open(filename, "r") as f:
            project = json.load(f)
        print(f"✓ Project loaded from {filename}")
        return project

    @staticmethod
    def extract_geometry_summary(project_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key geometric properties from project"""
        curve = project_dict["curve"]
        vault = project_dict["vault"]

        summary = {
            "project_name": project_dict["project_name"],
            "deployment_angle_deg": project_dict["deployment_angle"] * 180 / np.pi,
            "curve": {
                "num_points": curve["num_points"],
                "total_arc_length": float(curve["arc_length_params"][-1])
                if curve["arc_length_params"]
                else 0.0,
                "mean_curvature": float(np.mean(curve["curvatures"])),
                "mean_torsion": float(np.mean(curve["torsions"])),
            },
            "vault": {
                "num_creases": vault["num_creases"],
                "strip_width": vault["strip_width"],
                "strip_thickness": vault["strip_thickness"],
                "plane_distance": vault["plane_distance"],
                "total_vertices": sum(c["num_vertices"] for c in vault["creases"]),
                "total_faces": sum(c["num_faces"] for c in vault["creases"]),
            },
        }
        return summary

    @staticmethod
    def export_summary_to_file(
        project_dict: Dict[str, Any],
        filename: str = "project_summary.json",
    ):
        """Export geometry summary to separate JSON"""
        summary = CCUProjectSerializer.extract_geometry_summary(project_dict)
        with open(filename, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"✓ Summary exported to {filename}")
