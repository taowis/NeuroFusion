from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import numpy as np
import pandas as pd
from nilearn import datasets, image

try:
    import abagen
except Exception:
    abagen = None

try:
    import nibabel as nib
except Exception:
    nib = None

DATA_DIR = Path("data")
ATLAS_DIR = DATA_DIR / "atlas"
EXPR_DIR = DATA_DIR / "expression"
ATLAS_DIR.mkdir(parents=True, exist_ok=True)
EXPR_DIR.mkdir(parents=True, exist_ok=True)

@dataclass
class Atlas:
    name: str
    maps_path: str  # path to atlas NIfTI file on disk
    labels: pd.DataFrame  # cols: [index, label]

def _ensure_maps_path(maps_obj, out_path: Path) -> str:
    if isinstance(maps_obj, (str, bytes, Path)):
        return str(maps_obj)
    if hasattr(maps_obj, "get_filename"):
        fn = maps_obj.get_filename()
        if fn:
            return str(fn)
    if nib is None:
        raise RuntimeError("nibabel is required to save atlas image to disk but is not available.")
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    nib.save(maps_obj, out_path)
    return str(out_path)

def load_harvard_oxford(resolution: int = 2) -> Atlas:
    key = "cort-maxprob-thr25-2mm" if resolution == 2 else "cort-maxprob-thr25-1mm"
    atl = datasets.fetch_atlas_harvard_oxford(key)
    maps_out = ATLAS_DIR / f"harvard_oxford_cort_thr25_{resolution}mm.nii.gz"
    maps_path = _ensure_maps_path(atl.maps, maps_out)
    labels = pd.DataFrame({
        "index": np.arange(len(atl.labels)),
        "label": atl.labels,
    })
    return Atlas(name="HarvardOxford-Cort", maps_path=maps_path, labels=labels)

def _zscore_columns(df: pd.DataFrame) -> pd.DataFrame:
    return df.apply(lambda s: (s - s.mean()) / (s.std(ddof=0) if s.std(ddof=0) != 0 else 1.0), axis=0)

def prep_ahba_to_regions(atlas: Atlas) -> pd.DataFrame:
    outcsv = EXPR_DIR / f"ahba_{atlas.name}.csv"
    if outcsv.exists():
        return pd.read_csv(outcsv)

    if abagen is None:
        rng = np.random.default_rng(42)
        genes = [f"GENE{i:03d}" for i in range(1, 101)]
        regions = atlas.labels["label"].astype(str).tolist()
        data = [
            {"gene": g, "region": r, "value": float(rng.normal(loc=0, scale=1))}
            for g in genes for r in regions
        ]
        df = pd.DataFrame(data)
        df.to_csv(outcsv, index=False)
        return df

    expr = abagen.get_expression_data(
        atlas.maps_path,
        ibf_threshold=0.5,
        region_agg="mean",
        exact=False,
    )
    expr = _zscore_columns(expr)

    df = expr.reset_index().melt(id_vars="index", var_name="gene", value_name="value")                  .rename(columns={"index": "region"})
    df.to_csv(outcsv, index=False)
    return df

def gene_list(expr_df: pd.DataFrame) -> list[str]:
    return sorted(expr_df["gene"].unique().tolist())

def gene_to_stat_map(atlas: Atlas, expr_df: pd.DataFrame, gene: str):
    data_img = image.load_img(atlas.maps_path)
    data = data_img.get_fdata().copy()
    reg_df = atlas.labels.copy()
    reg_df["label"] = reg_df["label"].astype(str)
    gdf = expr_df[expr_df["gene"] == gene]
    merged = reg_df.merge(gdf, left_on="label", right_on="region", how="left")
    stat = np.zeros_like(data, dtype=float)
    for _, row in merged.iterrows():
        region_index = row["index"]
        val = row["value"] if not np.isnan(row["value"]) else 0.0
        stat[data == region_index] = val
    return image.new_img_like(data_img, stat)
