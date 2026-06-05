from matplotlib.pyplot import colormaps
import pandas as pd 
def get_int_input(prompt, default):
    value = input(f"{prompt} [default: {default}]: ").strip()
    if value == "":
        return default
    try:
        return int(value)
    except ValueError:
        print("Invalid input, using default.")
        return default
    
# Function to extract ensembles by identifying changes in ens column
# boundaries occur when ens_col value changes. 
# We also check that the change in z (delta_z) is greater than the change in ens_col to ensure we are capturing actual ensemble boundaries rather than noise.
def extract_ens(cl_df, ens_col):
    df = cl_df.copy()
    df['delta_z'] = df['Points:2'].diff()
    df['diff'] = df[ens_col].diff()

    nonzero_rows=pd.concat([df.iloc[:1],df[df['diff'].abs() >0]])
    nonzero_rows['delta_z'] = nonzero_rows['Points:2'].diff()

    df_aligned = df.reindex(nonzero_rows.index)
    
    mask = nonzero_rows['delta_z'] > df_aligned['delta_z']

    ens_df = nonzero_rows.loc[mask, [ ens_col, 'diff', 'delta_z','Points:2']].copy()
    ens_df['OF axial index'] = ens_df.index
    ens_df = ens_df.reset_index(drop=True)
    ens_df['rows_between'] = ens_df['OF axial index'].diff().fillna(0).astype(int)
    return ens_df
