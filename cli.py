import argparse
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import json


def parse_arguments():
    """Parse CLI arguments for CCU simulator"""
    parser = argparse.ArgumentParser(
        description="CCU (Curved Crease Unit) Simulator - Phase 1A",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py --input curve.json --num-creases 5 --width 8.0
  python cli.py --curve-file mycrease.txt --deploy 45 --export-all
  python cli.py --config project.json --output myproject
        """,
    )

    # Input options
    input_group = parser.add_argument_group("Input")
    input_group.add_argument(
        "--curve-file",
        type=str,
        default=None,
        help="Path to curve data file (JSON or TXT with points)",
    )
    input_group.add_argument(
        "--config",
        type=str,
        default=None,
        help="Load existing CCU project config (JSON)",
    )

    # Geometry parameters
    geom_group = parser.add_argument_group("Geometry")
    geom_group.add_argument(
        "--num-creases",
        type=int,
        default=5,
        help="Number of parallel crease planes (default: 5)",
    )
    geom_group.add_argument(
        "--width",
        type=float,
        default=5.0,
        help="Strip half-width in mm (default: 5.0)",
    )
    geom_group.add_argument(
        "--thickness",
        type=float,
        default=1.0,
        help="Plate thickness in mm (default: 1.0)",
    )
    geom_group.add_argument(
        "--plane-distance",
        type=float,
        default=10.0,
        help="Distance between crease planes in mm (default: 10.0)",
    )

    # Deployment
    deploy_group = parser.add_argument_group("Deployment")
    deploy_group.add_argument(
        "--deploy",
        type=float,
        default=0.0,
        help="Deployment angle α in degrees (0=flat, 90=fully open)",
    )
    deploy_group.add_argument(
        "--alternating",
        action="store_true",
        default=True,
        help="Enable alternating ridge/valley (default: True)",
    )
    deploy_group.add_argument(
        "--no-alternating",
        action="store_false",
        dest="alternating",
        help="Disable alternating pattern",
    )

    # Export options
    export_group = parser.add_argument_group("Export")
    export_group.add_argument(
        "--output",
        type=str,
        default="output",
        help="Output basename (without extension) (default: output)",
    )
    export_group.add_argument(
        "--export-dxf",
        action="store_true",
        help="Export 2D flat pattern to DXF",
    )
    export_group.add_argument(
        "--export-obj",
        action="store_true",
        help="Export 3D mesh to OBJ",
    )
    export_group.add_argument(
        "--export-stl",
        action="store_true",
        help="Export 3D mesh to STL (binary)",
    )
    export_group.add_argument(
        "--export-json",
        action="store_true",
        help="Export project data to JSON",
    )
    export_group.add_argument(
        "--export-all",
        action="store_true",
        help="Export all formats (DXF, OBJ, STL, JSON)",
    )

    # Advanced options
    adv_group = parser.add_argument_group("Advanced")
    adv_group.add_argument(
        "--resolution",
        type=int,
        default=100,
        help="Curve discretization resolution (default: 100)",
    )
    adv_group.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed logging",
    )
    adv_group.add_argument(
        "--validate",
        action="store_true",
        help="Run validation checks on output",
    )

    return parser.parse_args()


def print_banner():
    """Print welcome banner"""
    print("=" * 70)
    print(" CCU (Curved Crease Unit) Simulator - Phase 1A")
    print(" Corrugated Curved Unit Vault with Multi-Crease Geometry")
    print("=" * 70)
    print()


def print_summary(config: Dict[str, Any]):
    """Print configuration summary"""
    print("Configuration Summary:")
    print("-" * 70)
    print(f"  Curve resolution:    {config.get('resolution', 100)} points")
    print(f"  Number of creases:   {config.get('num_creases', 5)}")
    print(f"  Strip width:         {config.get('width', 5.0)} mm")
    print(f"  Strip thickness:     {config.get('thickness', 1.0)} mm")
    print(f"  Plane distance:      {config.get('plane_distance', 10.0)} mm")
    print(f"  Deployment angle:    {config.get('deploy', 0.0)}°")
    print(f"  Alternating:         {config.get('alternating', True)}")
    print("-" * 70)
    print()


def build_export_formats(args) -> list:
    """Determine which export formats to use"""
    formats = []
    if args.export_all:
        return ["dxf", "obj", "stl", "json"]
    if args.export_dxf:
        formats.append("dxf")
    if args.export_obj:
        formats.append("obj")
    if args.export_stl:
        formats.append("stl")
    if args.export_json:
        formats.append("json")
    return formats if formats else []


if __name__ == "__main__":
    print_banner()
    args = parse_arguments()

    config = {
        "num_creases": args.num_creases,
        "width": args.width,
        "thickness": args.thickness,
        "plane_distance": args.plane_distance,
        "deploy": args.deploy,
        "alternating": args.alternating,
        "resolution": args.resolution,
    }

    print_summary(config)

    export_formats = build_export_formats(args)
    if export_formats:
        print(f"Export formats: {', '.join(export_formats)}")
    else:
        print("No export formats specified (use --export-all or individual flags)")

    print("\n✓ CLI configuration ready. Call from main.py with these arguments.")
