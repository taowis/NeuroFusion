import argparse
from nilearn import datasets

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--resolution", type=int, default=2, choices=[1,2])
    args = ap.parse_args()
    key = "cort-maxprob-thr25-2mm" if args.resolution == 2 else "cort-maxprob-thr25-1mm"
    print(f"Fetching Harvard–Oxford cortical atlas ({args.resolution}mm)...")
    atlas = datasets.fetch_atlas_harvard_oxford(key)
    print("Saved:", atlas.maps)
