import argparse
from app.data_loader import load_harvard_oxford, prep_ahba_to_regions

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--atlas", default="harvard_oxford")
    ap.add_argument("--resolution", type=int, default=2)
    args = ap.parse_args()

    atlas = load_harvard_oxford(resolution=args.resolution)
    df = prep_ahba_to_regions(atlas)
    print(df.head())
    print("Saved to data/expression/")
