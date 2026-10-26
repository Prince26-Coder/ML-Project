# Spatio-temporal Clustering of Earthquakes in the Himalayan Region

**Student:** Prince  
**University Roll No.:** 24020570051  
**Assigned Problem No.:** 59  
**Domain:** Disaster Management  
**Methods:** K-means, hierarchical clustering with haversine distance, Gutenberg–Richter magnitude-frequency regression

> T> This repository is designed around the assigned problem in the provided project-allocation workbook. It does not copy the results in the sample AQI paper.
>
> The analysis has been executed on the selected earthquake catalogue. Numerical results are recorded in the generated output files in `results/`. The report discusses these outputs and their limitations.

## Research objectives

1. Identify spatial clusters of earthquake epicentres in the Himalayan region.
2. Compare K-means clustering with hierarchical clustering using haversine distance.
3. Examine the Gutenberg–Richter magnitude-frequency relationship and report the R² of its fitted linear regression.
4. Discuss how these results can support regional hazard analysis, while making clear that clusters are not earthquake predictions.

## Data

The allocation spreadsheet names the National Center for Seismology (NCS) Data Portal as the primary source:
- https://seismo.gov.in/data-portal

It also suggests the USGS Earthquake Catalog as an easier CSV export route:
- https://earthquake.usgs.gov/earthquakes/search/

For the USGS catalog, choose a date range and the Himalayan region, then export CSV. Save the file as `data/earthquakes.csv`. Recommended search area for an initial study (adjust and document this in the report): latitude 25–38° N, longitude 70–100° E. Choose and report a time period and magnitude threshold appropriate to the amount of available data.

Expected USGS columns include `time`, `latitude`, `longitude`, `depth`, `mag`, and `place`. The script accepts common variants of these names. NCS exports may use a different schema; rename the equivalent columns to these names or update the column map in the script.

## Install and run

Python 3.10+ recommended.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
python src/run_analysis.py
```

The script writes generated outputs into `results/`:
- `cleaned_earthquakes.csv`
- `cluster_metrics.csv`
- `gutenberg_richter_summary.json`
- `gutenberg_richter_curve.png`
- `earthquake_clusters.png`
- `magnitude_distribution.png`
- `analysis_summary.json`

If the Silhouette score cannot be calculated (for example, a cluster assignment has only one cluster or every sample is its own cluster), the script records it as unavailable rather than inventing a score.

## Methods

### Spatial clustering
K-means uses standardised latitude, longitude, depth and magnitude features. Hierarchical agglomerative clustering uses haversine distance between epicentres; depth and magnitude are then available for interpreting the resulting spatial clusters. Its Silhouette score is computed from haversine spatial distances. The K-means Silhouette score is computed in its standardised four-feature space, so the two scores use different distance definitions and should be compared cautiously. For very large datasets, the full pairwise distance matrix can use substantial memory, so the script caps the hierarchical evaluation sample and reports the sample size used.

Depth and magnitude are included in the exported cleaned dataset and can be explored in cluster summaries. Geographic clustering itself uses epicentre coordinates so the resulting clusters remain interpretable as spatial zones. This distinction should be stated in the report.

### Gutenberg–Richter relationship
The Gutenberg–Richter relation is commonly written as:

`log10(N(M >= m)) = a - b*m`

where `N` is the number of earthquakes at or above magnitude `m`, `a` is an intercept and `b` is the slope magnitude. The script fits a simple linear regression to the empirical cumulative magnitude-frequency curve for a documented magnitude range. The fit depends on catalogue completeness and the selected time period; R² should not be interpreted as proof of forecasting skill.

## Important limitations

- A cluster is a statistical grouping, not an official seismic hazard boundary.
- Earthquakes are not predicted by this analysis; it does not forecast when or where the next earthquake will occur.
- Catalog completeness, reporting thresholds, aftershock sequences, spatial coverage and the chosen date window can affect results.
- A regional case study should compare model outputs with credible seismological literature and clearly state its geographic/time filters.

## Repository structure

```text
ML-Project/
├── data/
│   └── earthquakes.csv
├── report/
│   └── journal_report_template.md
├── results/
│   ├── earthquake_clusters.png
│   ├── magnitude_distribution.png
│   ├── gutenberg_richter_curve.png
│   ├── cluster_metrics.csv
│   ├── gutenberg_richter_summary.json
│   ├── analysis_summary.json
│   └── cleaned_earthquakes.csv
├── src/
│   └── run_analysis.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Citation and academic integrity

Cite the exact catalogue provider, access date, query filters, time range and any data transformations in the final report. Follow your college's policy on AI-assisted work. Do not submit placeholder values as measured results; run the code and use the generated output files.
