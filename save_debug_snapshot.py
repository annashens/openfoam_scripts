#!/usr/bin/env python3
from paraview.simple import *
import os
from datetime import datetime
import subprocess

# -------------------------------
# Determine Git root (run from scripts/ but paths relative to repo root)
# -------------------------------
try:
    REPO_ROOT = subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"],
        universal_newlines=True
    ).strip()
except subprocess.CalledProcessError:
    raise RuntimeError("Could not determine Git root. Are you inside a Git repo?")

# Change working directory to Git root
os.chdir(REPO_ROOT)

# -------------------------------
# User input
# -------------------------------
date_str = datetime.now().strftime("%d%b%Y").lower()

output_dir_input = input("Enter output directory (default: debug_logs): ").strip()
output_dir_input = "debug_logs" if not output_dir_input else output_dir_input
if output_dir_input not in ["debug_logs", "case_data"]:
    if output_dir_input is None:
        output_dir_input = "debug_logs"
    else:
        raise ValueError("Invalid output directory. Must be 'debug_logs' or 'case_data'.")
snapshot_id = input("Enter debug index: ").strip()
state_str = input("Enter state file: ").strip()
snapshot_folder = f"{snapshot_id}_{date_str}/snapshots/{state_str}"

# Output directory
output_dir = os.path.join("user_data", output_dir_input, snapshot_folder)
os.makedirs(output_dir, exist_ok=True)
print(f"Snapshots will be saved in: {output_dir}")

t_max_input = input("Enter max time (or leave blank for all): ").strip()
t_skip_input = input("Enter time skip (integer, default 1): ").strip()

t_max = float(t_max_input) if t_max_input else None
t_skip = int(t_skip_input) if t_skip_input else 1

# -------------------------------
# File paths
# -------------------------------
foam_file = "case.foam"                  # OpenFOAM case
state_file = os.path.join("states", f"{state_str}.pvsm")     # ParaView state file

# -------------------------------
# Load ParaView state
# -------------------------------
LoadState(state_file)

# -------------------------------
# Find first OpenFOAM reader
# -------------------------------
sources = GetSources()
reader = None
for key, src in sources.items():
    if src.SMProxy.GetXMLName() == "OpenFOAMReader":
        reader = src
        break
if reader is None:
    raise RuntimeError("No OpenFOAM reader found in the state file.")

print(f"Using reader: {reader.SMProxy.GetXMLLabel()}")

# Point reader to the new case
reader.FileName = foam_file

# -------------------------------
# Render view setup
# -------------------------------
layout = GetLayout()  # capture full layout
render_view = GetActiveViewOrCreate("RenderView")
render_view.ResetCamera()

# -------------------------------
# Get all timesteps and apply filters
# -------------------------------
times = reader.TimestepValues
if t_max is not None:
    times = [t for t in times if t <= t_max]

times = times[::t_skip]
print(f"Rendering {len(times)} timesteps (after applying t_max={t_max} and t_skip={t_skip})")

# -------------------------------
# Loop over timesteps (fixed for multiple subplots)
# -------------------------------
all_views = GetViews()  # get all views in the layout

for t in times:
    print(f"Rendering time: {t}")

    # Update all views
    for view in all_views:
        view.ViewTime = t

    # Update all sources for all views
    for src in sources.values():
        try:
            src.UpdatePipeline(t)
        except:
            pass  # some sources may not support timesteps

    # Update 3D representation (only for main reader)
    rep = GetDisplayProperties(reader, view=render_view)
    # try:
    #     if rep is not None and "U" in reader.CellArrays.Available:
    #         ColorBy(rep, ("CELLS", "U"))
    #         rep.RescaleTransferFunctionToDataRange(True, False)
    # except AttributeError:
    #     print(f"Skipping coloring at time {t}, unsupported representation.")

    # Render and save screenshot (full layout)
    RenderAllViews()
    fname = os.path.join(output_dir, f"{t:.4f}.png")
    SaveScreenshot(fname, layout)

print("All snapshots saved successfully!")