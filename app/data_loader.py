from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd
from nilearn import datasets, image

try:
    import abagen
except Exception as e:  # allow app to run without abagen for demo
    abagen = None

DATA_DIR = Path("data")
ATLAS_DIR = DATA_DIR / "atlas"
EXPR_DIR = DATA_DIR / "expression"
ATLAS_DIR.mkdir(parents=True, exist_ok=True)
EXPR_DIR.mkdir(parents=True, exist_ok=True)

@dataclass
class Atlas:
    name: str
    maps_nii: Path
    labels: pd.DataFrame  # columns: [index, label]

def load_harvard_oxford(resolution: int = 2) -> Atlas:
    atlas = datasets.fetch_atlas_harvard_oxford("cort-maxprob-thr25-2mm") if resolution == 2 else datasets.fetch_atlas_harvard_oxford("cort-maxprob-thr25-1mm")
    labels = pd.DataFrame({
        "index": np.arange(len(atlas.labels)),
        "label": atlas.labels,
    })
    return Atlas(
        name="HarvardOxford-Cort",
        maps_nii=Path(atlas.maps),
        labels=labels,
    )

def prep_ahba_to_regions(atlas: Atlas) -> pd.DataFrame:
    """Return a long table: columns [gene, region, value]. If abagen is missing, mock data."""
    outcsv = EXPR_DIR / f"ahba_{atlas.name}.csv"
    if outcsv.exists():
        return pd.read_csv(outcsv)

    if abagen is None:
        # Demo fallback: create synthetic expressions for 100 genes × N regions
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

    # Real aggregation path using abagen
    # Map tissue samples to atlas, then aggregate by region
    # abagen.get_expression_data returns regions × genes matrix by default
    expr = abagen.get_expression_data(
        atlas.maps_nii.as_posix(),
        ibf_threshold=0.5,
        region_agg="mean",
        donor_norm=True,
        gene_norm=True,
        exact=False,
        lr_mirror=True,
    )
    df = expr.reset_index().melt(id_vars="index", var_name="gene", value_name="value").rename(columns={"index": "region"})
    df.to_csv(outcsv, index=False)
    return df

def gene_list(expr_df: pd.DataFrame) -> list[str]:
    return sorted(expr_df["gene"].unique().tolist())

def gene_to_stat_map(atlas: Atlas, expr_df: pd.DataFrame, gene: str):
    """Convert region values for a gene into a 3D NIfTI by painting atlas regions."""
    data_img = image.load_img(atlas.maps_nii)
    data = data_img.get_fdata().copy()

    # Build region index → value map
    reg_df = atlas.labels.copy()
    reg_df["label"] = reg_df["label"].astype(str)
    gdf = expr_df[expr_df["gene"] == gene]
    merged = reg_df.merge(gdf, left_on="label", right_on="region", how="left")

    # New volume initialized to zeros
    stat = np.zeros_like(data, dtype=float)
    for idx, row in merged.iterrows():
        region_index = row["index"]
        val = row["value"] if not np.isnan(row["value"]) else 0.0
        stat[data == region_index] = val

    return image.new_img_like(data_img, stat)
