from python.helpers.paths import remove_system_paths
remove_system_paths()
import os
import glob
import re
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

import argparse
def reduce_csv_files(
    outDir,
    unwanted_prefixes=None,
    save_cleaned_csv=False,
    delete_original=False,
    use_streaming=False
):
    remove_system_paths()
    unwanted_prefixes = unwanted_prefixes or ["ddt"]

    csv_files = sorted(glob.glob(os.path.join(outDir, "cells_t*.csv")))
    if not csv_files:
        print(f"No CSV files found in {outDir}")
        return

    points_saved = False
    cleaned_files = []
    files_to_delete = []  # <-- keep track of originals to delete later

    if use_streaming:
        parquet_file = os.path.join(outDir, "all_timesteps.parquet")
        parquet_writer = None

    for f in csv_files:
        df = pd.read_csv(f)

        # Save points once
        if not points_saved:
            points = df[["Points:0","Points:1","Points:2"]]
            points.to_csv(os.path.join(outDir, "points.csv"), index=False)
            points_saved = True
            print(f"Wrote points.csv")

        # Drop unwanted columns (keep coordinates)
        cols_to_drop = [c for c in df.columns if any(c.startswith(p) for p in unwanted_prefixes)]
        df = df.drop(columns=cols_to_drop)

        # Save cleaned CSV if requested
        if save_cleaned_csv:
            clean_fname = os.path.join(outDir, "cleaned_" + os.path.basename(f))
            df.to_csv(clean_fname, index=False)
            cleaned_files.append(clean_fname)
            print(f"Saved cleaned CSV: {clean_fname}")

        # Add time column
        t_match = re.search(r"cells_t([0-9.]+)\.csv", f)
        if t_match:
            df['time'] = float(t_match.group(1))

        # Streaming write
        if use_streaming:
            table = pa.Table.from_pandas(df)
            if parquet_writer is None:
                parquet_writer = pq.ParquetWriter(parquet_file, table.schema)
            parquet_writer.write_table(table)
            print(f"Appended {f} to Parquet")

        # Mark file for deletion **after all Parquet work**
        if delete_original:
            files_to_delete.append(f)

    # Finish streaming
    if use_streaming and parquet_writer:
        parquet_writer.close()
        print(f"Saved streaming Parquet: {parquet_file}")
    elif not use_streaming:
        # In-memory concatenation
        try:
            all_dfs = []
            for f in cleaned_files if save_cleaned_csv else csv_files:
                df = pd.read_csv(f)
                t_match = re.search(r"cells_t([0-9.]+)\.csv", f)
                if t_match:
                    df['time'] = float(t_match.group(1))
                all_dfs.append(df)

            combined = pd.concat(all_dfs, ignore_index=True)
            parquet_file = os.path.join(outDir, "all_timesteps.parquet")
            combined.to_parquet(parquet_file, index=False)
            print(f"Saved {parquet_file}")

        except MemoryError:
            print("\nERROR: Not enough RAM to concatenate all timesteps at once.")
            print("Switch `use_streaming=True` to use streaming Parquet instead.")

    # Delete originals **after everything**
    for f in files_to_delete:
        os.remove(f)
        print(f"Deleted original CSV: {f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("outDir")
    parser.add_argument("--save-cleaned", action="store_true")
    parser.add_argument("--delete-original", action="store_true")
    parser.add_argument("--drop-prefixes", nargs="*", default=["ddt"])
    parser.add_argument("--use-streaming", action="store_true")  # <--- optional flag
    args = parser.parse_args()

    reduce_csv_files(
        outDir=args.outDir,
        unwanted_prefixes=args.drop_prefixes,
        save_cleaned_csv=args.save_cleaned,
        delete_original=args.delete_original,
        use_streaming=args.use_streaming
    )