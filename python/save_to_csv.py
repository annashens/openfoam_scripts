from paraview.simple import *
import os
import sys

# --- get output directory from bash ---
if len(sys.argv) < 2:
    print("Usage: pvpython save_to_csv.py <output_dir>")
    sys.exit(1)

outDir = sys.argv[1]
os.makedirs(outDir, exist_ok=True)

case = OpenFOAMReader(FileName="case.foam")
case.MeshRegions = ['internalMesh']

# Enable all arrays safely./
case.CellArrays  = case.CellArrays.Available
case.PointArrays = case.PointArrays.Available

UpdatePipeline()

for t in case.TimestepValues:
    UpdatePipeline(time=t, proxy=case)

    fname = os.path.join(outDir, f"cells_t{t:.6f}.csv")

    SaveData(
        fname,
        proxy=case,
        Precision=10
    )

    print(f"Wrote {fname}")
