from python.helpers.paths import remove_system_paths
remove_system_paths()
import numpy as np
import pandas as pd
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager

from python.helpers.general import extract_ens
from python.helpers.sample import axial_cutline
from python.helpers.general import get_int_input


DEFAULT_DATA_PATH = 'backup/debug/8_17feb2026/csv/cells_t1.12698e-05.csv'
df_path = get_int_input("Enter path to all.csv with point data", DEFAULT_DATA_PATH)

output_folder = 'openfoam_scripts/python/output/'
fig_name = 'ensemble_map.png'

df=pd.read_csv(df_path)

cl_df = axial_cutline(df,0).sort_values(by=['Points:2'])
core_ens = extract_ens(cl_df, ens_col='CoreEnsembles')
ens_df = extract_ens(cl_df, ens_col='EnsembleLables')
core_bounds = core_ens['Points:2'].tolist()

phi_col = 'EnsembleLables'
phi = df[phi_col]

# Extract coordinates and temperature
num_levels=int((len(phi.unique())+1)/2)
fig, ax = plt.subplots(1, 1, figsize=(4,6))
sc = ax.tricontourf(
    df["Points:0"], df["Points:2"], phi,
    levels=num_levels,
    cmap="viridis",
    vmin=phi[phi > 0].min(),
    vmax=phi.max(),
    extend='max'
)
cbar = fig.colorbar(sc, ax=ax)
cbar.set_label(phi_col, fontsize=9)

ax.set_xlabel("x")
ax.set_ylabel("z")

core_bounds = core_ens['Points:2'].tolist()
for i,y in enumerate(core_bounds): 
    if i==0:
        label_str="Core Partition"
    else:
        label_str=""
    ax.axhline(y, color="orangered", linestyle="-", linewidth=1, label=label_str)
sub_bounds=ens_df['Points:2'].tolist()
for i,y in enumerate(sub_bounds): 
    if i==0:
        label_str="Subdivisions"
    else:
        label_str=""
    ax.axhline(y, color="gray", linestyle="--", linewidth=0.8, label=label_str) 
legend_title_font = font_manager.FontProperties(weight='semibold', size=10)

handles, labels = ax.get_legend_handles_labels()
fig.legend(
        loc='upper center', bbox_to_anchor=(0.5, 0), ncol=3, fontsize=9,
        title='Legend', title_fontproperties=legend_title_font
    )

num_core_div = len(core_ens)+1
num_subdiv= int(num_core_div/len(ens_df)+1)
fig.suptitle(f"Modified Ensembles: \n {num_core_div} Core Partitions, {num_subdiv} Subdivisions Per Core", fontsize=10)
fig.tight_layout()


fig.savefig(output_folder+fig_name)