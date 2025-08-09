from pathlib import Path
from nilearn import datasets

if __name__ == "__main__":
    print("Fetching Harvard–Oxford cortical atlas (2mm)...")
    atlas = datasets.fetch_atlas_harvard_oxford("cort-maxprob-thr25-2mm")
    print("Saved:", atlas.maps)
