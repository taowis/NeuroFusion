from __future__ import annotations
from pathlib import Path
import tempfile
import pandas as pd
from nilearn import plotting

CACHE_DIR = Path(".data_cache")
CACHE_DIR.mkdir(exist_ok=True)

def cache_path(name: str) -> Path:
    return CACHE_DIR / name

def save_stat_map_img(img_nii, title: str = "stat map") -> Path:
    tmpdir = Path(tempfile.mkdtemp())
    out_png = tmpdir / "stat_map.png"
    display = plotting.plot_stat_map(img_nii, title=title, display_mode="ortho")
    display.savefig(out_png)
    display.close()
    return out_png

def normalize_series(s: pd.Series) -> pd.Series:
    s = s.astype(float)
    rng = s.max() - s.min()
    if rng == 0:
        return s - s.min()
    return (s - s.min()) / rng
