# NeuroFusion

Interactive dashboard that fuses **brain transcriptomics** (Allen Human Brain Atlas, AHBA) with **neuroimaging atlases** (e.g., Harvard–Oxford in MNI space) for region-wise exploration.

## Features (MVP)
- Gene selector with region-wise expression overlay
- Brain map preview (nilearn) and bar chart by region
- Downloadable CSV summaries

## Quickstart
```bash
# 1) Create env and install
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2) Fetch atlas + prep expression (cached under data/)
python scripts/fetch_atlas.py
python scripts/prep_ahba_regions.py --atlas harvard_oxford --resolution 2

# 3) Run dashboard
streamlit run app/dashboard.py
```

## Data notes
- AHBA processing uses [`abagen`](https://abagen.readthedocs.io/). First run downloads ~GBs and caches on disk.
- Harvard–Oxford atlas is fetched via `nilearn.datasets`.

## Repo layout
See comments in each file; `app/data_loader.py` centralizes data I/O.

## License
MIT (see `LICENSE`). Cite the Allen Institute + atlas authors when publishing.
