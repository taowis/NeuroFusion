import argparse
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from app.data_loader import load_harvard_oxford, prep_ahba_to_regions

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--resolution", type=int, default=2, choices=[1,2])
    args = ap.parse_args()
    atlas = load_harvard_oxford(resolution=args.resolution)
    df = prep_ahba_to_regions(atlas)
    print(df.head())
    print("Saved CSV to data/expression/")
