# CCU Simulator

**Curved-Crease Unfoldable (CCU) Python Simulator**

A computational framework for designing, analyzing, and fabricating curved-crease flat-foldable bending-active plate structures.

## Phase 1A: Core Geometry Engine

- Discrete differential geometry (Frenet-Serret frame)
- DFS (Discrete Folding Symmetry) ruling computation
- Single and multi-crease corrugation
- Deployment kinematics (Eq. 8)
- 2D flat-pattern export for CNC/laser cutting
- 3D mesh export (STL, OBJ)

## Quick Start

```bash
pip install -r requirements.txt
python examples/simple_arc.py
```

## Project Structure

```
ccu-simulator/
├── core/
│   ├── __init__.py
│   ├── curve_analysis.py       # Discretization + Frenet-Serret
│   ├── rulings.py              # DFS, ruling angle correlation
│   ├── mesh_topology.py        # Quad mesh construction
│   ├── thickness.py            # Axis-shift offset
│   ├── deployment.py           # Eq. (8): κ2D → κ3D via α
│   └── multi_crease.py         # Multi-crease vault arrays
├── export/
│   ├── __init__.py
│   ├── dxf_export.py           # Flat patterns → DXF
│   ├── mesh_export.py          # 3D → STL/OBJ
│   └── json_export.py          # Full geometry + metadata
├── parametric/
│   ├── __init__.py
│   ├── configs.py              # Configuration trees
│   └── generators.py           # High-level builders
├── visualization/
│   ├── __init__.py
│   └── viewer.py               # Matplotlib/PyVista plots
├── tests/
│   ├── __init__.py
│   ├── test_frenet.py
│   ├── test_dfs.py
│   └── test_deployment.py
├── examples/
│   ├── simple_arc.py           # Single crease, arc profile
│   ├── multi_crease_vault.py   # Multi-crease corrugation
│   └── variable_ruling.py      # Variable ruling angles
├── requirements.txt
└── README.md
```

## Research References

Scheder-Bieschin, L., Van Mele, T., & Block, P. (2023). Curved-Crease Flat-Foldable Bending-Active Plate Structures. In *Advances in Architectural Geometry 2023*.

- **Eq. (1)-(4):** Crease torsion and reflection angle
- **Eq. (5):** Deployment curvature relationship
- **Eq. (6)-(8):** Discrete deployment kinematics
- **Sec. 4.2:** Special cases (planar creases, constant reflection angle)
- **Sec. 5.3:** Axis-shift thickness approach
