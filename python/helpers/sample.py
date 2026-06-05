import numpy as np
import pandas as pd
from scipy.interpolate import griddata

def axial_cutline(df, r):
    rows = []
    x_vals = np.sort(df['Points:2'].unique())

    # selects data frame nearest cells rather than inerpolating
    for x in x_vals:
        # distance from target point (r, x)
        dist = np.sqrt(
            (df['Points:0'] - r)**2 +
            (df['Points:2'] - x)**2
        )
        # index of nearest cell
        idx = dist.idxmin()
        # store full row
        rows.append(df.loc[idx])

    return pd.DataFrame(rows).reset_index(drop=True)

def radial_cutline(df, x,columns):
    r_vals = np.sort(df['Points:0'].unique())
    # interpolats values
    interp_points = np.column_stack([r_vals, np.full_like(r_vals, x, dtype=float)])

    out = pd.DataFrame({
        'Points:0': r_vals,
        'Points:2': x
    })

    for col in columns:
        out[col] = griddata(
            df[['Points:0', 'Points:2']].values,
            df[col].values,
            interp_points,
            method='linear'
        )
    return out