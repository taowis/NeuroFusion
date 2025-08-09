from __future__ import annotations
import io
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from .data_loader import load_harvard_oxford, prep_ahba_to_regions, gene_list, gene_to_stat_map
from .utils import save_stat_map_img, normalize_series

st.set_page_config(page_title="NeuroFusion", layout="wide")
st.title("🧠 NeuroFusion: Transcriptomics × Atlas Explorer")

with st.sidebar:
    st.header("Options")
    res = st.selectbox("Atlas resolution", options=[2, 1], index=0, help="Harvard–Oxford maxprob cort atlas")
    st.caption("First run may download atlas and AHBA (~GB)")

# Load atlas + expression (cached)
atlas = load_harvard_oxford(resolution=res)
expr_df = prep_ahba_to_regions(atlas)

# Controls
gene = st.selectbox("Choose a gene", options=gene_list(expr_df))
normalize = st.toggle("Min–max normalize by region", value=True)

# Data slice for selected gene
gene_df = expr_df[expr_df["gene"] == gene].copy()
if normalize:
    gene_df["value_norm"] = normalize_series(gene_df["value"])
    value_col = "value_norm"
else:
    value_col = "value"

# Plot bar chart
left, right = st.columns([1, 1])
with left:
    st.subheader("Expression by Region")
    bar = px.bar(gene_df.sort_values(value_col, ascending=False), x="region", y=value_col, height=520)
    st.plotly_chart(bar, use_container_width=True)

# Create stat map and preview
stat_img = gene_to_stat_map(atlas, expr_df, gene)
img_path = save_stat_map_img(stat_img, title=f"{gene} expression (stat map)")
with right:
    st.subheader("Brain Map (stat overlay)")
    st.image(str(img_path))

# Download CSV
csv_buf = io.StringIO()
(gene_df[["gene", "region", value_col]].rename(columns={value_col: "value"}))         .to_csv(csv_buf, index=False)
st.download_button("Download CSV", data=csv_buf.getvalue(), file_name=f"{gene}_region_expression.csv", mime="text/csv")

st.caption("Data sources: Allen Human Brain Atlas via abagen; Harvard–Oxford atlas via nilearn.")
