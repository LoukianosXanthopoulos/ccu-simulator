import ezdxf
from typing import List, Tuple
from .curve_analysis import Point3d, Vector3d


def export_flat_pattern_dxf(
    centerline_points: List[Point3d],
    ruling_vectors: List[Tuple[Vector3d, Vector3d]],
    width: float,
    filename: str = "flat_pattern.dxf",
):
    """
    Export 2D flat crease pattern to DXF for CNC/laser cutting.
    Draws centerline + left/right edge curves.
    """
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()

    # Centerline
    centerline_2d = [(pt.x, pt.y) for pt in centerline_points]
    msp.add_lwpolyline(centerline_2d, dxfattribs={"layer": "centerline", "color": 1})

    # Left edge (centerline + width * R_left)
    left_edge_2d = [
        (
            pt.x + width * R_left.x,
            pt.y + width * R_left.y,
        )
        for pt, (R_left, R_right) in zip(centerline_points, ruling_vectors)
    ]
    msp.add_lwpolyline(left_edge_2d, dxfattribs={"layer": "left_edge", "color": 2})

    # Right edge (centerline + width * R_right)
    right_edge_2d = [
        (
            pt.x + width * R_right.x,
            pt.y + width * R_right.y,
        )
        for pt, (R_left, R_right) in zip(centerline_points, ruling_vectors)
    ]
    msp.add_lwpolyline(right_edge_2d, dxfattribs={"layer": "right_edge", "color": 3})

    doc.saveas(filename)
    print(f"✓ Flat pattern exported to {filename}")


def export_vault_dxf(
    vault_meshes,
    filename: str = "vault_pattern.dxf",
):
    """
    Export multi-crease vault as DXF (centerlines + edges for each crease).
    vault_meshes: List of MeshBuilder instances
    """
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()

    for crease_idx, mesh in enumerate(vault_meshes):
        layer_prefix = f"crease_{crease_idx}"
        
        # Extract centerline from mesh (vertices[0:n])
        n = len(mesh.centerline)
        centerline_2d = [(pt.x, pt.y) for pt in mesh.centerline]
        msp.add_lwpolyline(
            centerline_2d,
            dxfattribs={"layer": f"{layer_prefix}_center", "color": 1},
        )

        # Left and right edges
        left_2d = [(v.x, v.y) for v in mesh.vertices[n : 2 * n]]
        right_2d = [(v.x, v.y) for v in mesh.vertices[2 * n : 3 * n]]

        msp.add_lwpolyline(
            left_2d, dxfattribs={"layer": f"{layer_prefix}_left", "color": 2}
        )
        msp.add_lwpolyline(
            right_2d, dxfattribs={"layer": f"{layer_prefix}_right", "color": 3}
        )

    doc.saveas(filename)
    print(f"✓ Vault pattern exported to {filename}")
