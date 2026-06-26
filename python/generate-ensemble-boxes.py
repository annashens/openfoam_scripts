import numpy as np
import sys; print(sys.executable)
import pandas as pd
from helpers.sample import axial_cutline
from helpers.general import get_int_input
# path of csv with cell data points
# DEFAULT_DATA_PATH = 'postProcess/triage/2_15jun2026/csv/points.csv'
DEFAULT_DATA_PATH='postProcess/triage/33_18jun2026/csv/points.csv'
df_path = get_int_input("Enter path to all.csv with point data", DEFAULT_DATA_PATH)
output_folder = 'scripts/python/output/'
file_name = 'CoordinatesOfEnsembleBoxes.csv'

DEFAULT_NUM_SUBDIV = 2
DEFAULT_NUM_CORES = 16
num_subdiv = get_int_input("Enter number of subdivisions", DEFAULT_NUM_SUBDIV)
num_cores = get_int_input("Enter number of cores", DEFAULT_NUM_CORES)
total_ens = num_cores*num_subdiv
num_ens_boxes = total_ens - num_cores +1
print(f"Using {num_cores} cores and {num_subdiv} subdivisions:\n"
      +f"{total_ens}, defining {num_ens_boxes} ensemble boxes in {output_folder}/{file_name}")


all_df=pd.read_csv(df_path)
cl_df = axial_cutline(all_df, 0).sort_values(by=['Points:2'])

cl_df['main_bin'] = pd.qcut(cl_df['Points:2'], q=num_cores, labels=False)
cl_df['sub_bin'] = cl_df.groupby('main_bin')['Points:2'] \
                            .transform(lambda x: pd.qcut(x, q=num_subdiv, labels=False))
cl_df['final_bin'] = cl_df['main_bin']*num_subdiv + cl_df['sub_bin']

# Full aggregation
summary = (
    cl_df
    .groupby('final_bin')['Points:2']
    .agg(min='min', max='max', count='count', unique='nunique') # max -> upper bound, min -> lower bound
    .sort_index()
)

# keep only sub-bin rows for defining ensemble boxes
filtered_df = summary[summary.index % num_subdiv != 0].reset_index(drop=True)  # keep only sub-bin max rows
boundaries = list(filtered_df['min']) 

# boxes are defined based on 2 corners
rows = []
for i,b in enumerate(boundaries):
    rows.append([1000, 1000, b])
    rows.append([-1000, -1000, b])
    
df_csv = pd.DataFrame(rows)
df_csv.columns=['c1','c2','c3']
upper_bound = pd.DataFrame([{
    "c1": 1000,
    "c2": 1000,
    "c3": 1000
}])
lower_bound = pd.DataFrame([{
    "c1": -1000,
    "c2": -1000,
    "c3": -1000,
}])

df_csv = pd.concat([lower_bound, df_csv,upper_bound], ignore_index=True)

df_csv = df_csv.iloc[::-1].reset_index(drop=True) # reverse order

df_csv.to_csv(output_folder+file_name, index=False, header=False)
