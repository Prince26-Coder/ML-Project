from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy
import sklearn
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score
from sklearn.linear_model import LinearRegression
from sklearn.metrics.pairwise import haversine_distances

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
EARTH_RADIUS_KM = 6371.0088


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Map common USGS/NCS column names into a standard schema."""
    lower = {str(c).strip().lower(): c for c in df.columns}
    aliases = {
        "time": ["time", "origin_time", "datetime", "date", "origin time"],
        "latitude": ["latitude", "lat"],
        "longitude": ["longitude", "lon", "long"],
        "depth": ["depth", "depth_km", "depth (km)"],
        "mag": ["mag", "magnitude", "ml", "mw"],
        "place": ["place", "location", "region"],
    }
    rename = {}
    for standard, options in aliases.items():
        for opt in options:
            if opt in lower:
                rename[lower[opt]] = standard
                break
    df = df.rename(columns=rename)
    required = {"time", "latitude", "longitude", "mag"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"Could not find required columns {sorted(missing)}. "
            f"Found columns: {list(df.columns)}. Rename the source CSV columns to time, latitude, longitude, mag."
        )
    if "depth" not in df.columns:
        df["depth"] = np.nan
    if "place" not in df.columns:
        df["place"] = ""
    return df


def load_catalog(path: Path, bounds: tuple[float, float, float, float]) -> tuple[pd.DataFrame, dict]:
    raw = pd.read_csv(path)
    raw_count = len(raw)
    df = normalize_columns(raw)
    df["time"] = pd.to_datetime(df["time"], errors="coerce", utc=True)
    for col in ["latitude", "longitude", "depth", "mag"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["time", "latitude", "longitude", "mag"]).copy()
    min_lat, max_lat, min_lon, max_lon = bounds
    df = df[
        df["latitude"].between(min_lat, max_lat)
        & df["longitude"].between(min_lon, max_lon)
    ].copy()
    df = df.drop_duplicates(subset=["time", "latitude", "longitude", "mag"])
    if len(df) < 10:
        raise ValueError(
            f"Only {len(df)} records remain after cleaning and geographic filtering. "
            "Check your CSV and --bounds values."
        )
    df = df.sort_values("time").reset_index(drop=True)
    metadata = {
        "input_file": str(path),
        "input_rows": int(raw_count),
        "cleaned_rows_in_bounds": int(len(df)),
        "date_start_utc": str(df["time"].min()),
        "date_end_utc": str(df["time"].max()),
        "bounds_lat_lon": {"min_lat": min_lat, "max_lat": max_lat, "min_lon": min_lon, "max_lon": max_lon},
        "depth_missing_percent": float(df["depth"].isna().mean() * 100),
    }
    return df, metadata


def compute_silhouette(coords_radians: np.ndarray, labels: np.ndarray, sample_size: int = 3000):
    unique = np.unique(labels)
    if len(unique) < 2 or len(unique) >= len(labels):
        return None
    try:
        return float(silhouette_score(
            coords_radians, labels, metric="haversine",
            sample_size=min(sample_size, len(labels)), random_state=42
        ))
    except Exception:
        return None


def cluster_catalog(df: pd.DataFrame, k: int, hierarchical_max: int = 2500):
    coords_deg = df[["latitude", "longitude"]].to_numpy()
    coords_rad = np.radians(coords_deg)
    # K-means uses location, depth, and magnitude after standardising the
    # dimensions. Latitude/longitude are scaled in kilometres approximately;
    # depth and magnitude are standardised so their units do not dominate.
    from sklearn.preprocessing import StandardScaler
    km_features = df[["latitude", "longitude", "depth", "mag"]].copy()
    km_features["depth"] = km_features["depth"].fillna(km_features["depth"].median())
    km_scaled = StandardScaler().fit_transform(km_features.to_numpy(dtype=float))
    km = KMeans(n_clusters=k, n_init=10, random_state=42)
    km_labels = km.fit_predict(km_scaled)
    # Silhouette is calculated in the same scaled feature space used by K-means.
    km_sil = None
    if 1 < len(np.unique(km_labels)) < len(km_labels):
        try:
            km_sil = float(silhouette_score(
                km_scaled, km_labels,
                sample_size=min(3000, len(km_labels)), random_state=42
            ))
        except Exception:
            km_sil = None

    # Full pairwise distance matrix is O(n^2); use a deterministic sample if needed.
    rng = np.random.default_rng(42)
    if len(df) > hierarchical_max:
        sample_idx = np.sort(rng.choice(len(df), size=hierarchical_max, replace=False))
    else:
        sample_idx = np.arange(len(df))
    sample_rad = coords_rad[sample_idx]
    # sklearn haversine_distances returns angular distance in radians.
    distance_matrix = haversine_distances(sample_rad, sample_rad)
    try:
        hier = AgglomerativeClustering(
            n_clusters=k, metric="precomputed", linkage="average"
        )
    except TypeError:  # compatibility with older scikit-learn
        hier = AgglomerativeClustering(
            n_clusters=k, affinity="precomputed", linkage="average"
        )
    hier_labels = hier.fit_predict(distance_matrix)
    hier_sil = compute_silhouette(sample_rad, hier_labels)

    output = df.copy()
    output["kmeans_cluster"] = km_labels
    output["hierarchical_cluster"] = -1
    output.loc[sample_idx, "hierarchical_cluster"] = hier_labels

    metrics = pd.DataFrame([
        {"method": "K-means (standardised latitude, longitude, depth, magnitude)", "clusters": k,
         "silhouette_score": km_sil, "silhouette_distance": "Euclidean on standardised features",
         "evaluated_samples": int(len(df))},
        {"method": "Agglomerative (average linkage, haversine epicentre distance)", "clusters": k,
         "silhouette_score": hier_sil, "silhouette_distance": "Haversine on latitude/longitude",
         "evaluated_samples": int(len(sample_idx))},
    ])
    return output, metrics, int(len(sample_idx))


def fit_gutenberg_richter(df: pd.DataFrame, min_mag: float, max_mag: float, step: float):
    mags = df["mag"].to_numpy(dtype=float)
    thresholds = np.arange(min_mag, max_mag + step / 2, step)
    counts = np.array([(mags >= threshold).sum() for threshold in thresholds], dtype=int)
    valid = counts > 0
    x = thresholds[valid]
    y = np.log10(counts[valid])
    if len(x) < 3:
        raise ValueError("Not enough non-zero magnitude thresholds to fit Gutenberg–Richter regression.")
    model = LinearRegression().fit(x.reshape(-1, 1), y)
    pred = model.predict(x.reshape(-1, 1))
    r2 = float(model.score(x.reshape(-1, 1), y))
    summary = {
        "equation": "log10(N(M >= m)) = a - b*m",
        "intercept_a": float(model.intercept_),
        "slope": float(model.coef_[0]),
        "b_value_as_negative_slope": float(-model.coef_[0]),
        "r2": r2,
        "magnitude_threshold_min": float(x.min()),
        "magnitude_threshold_max": float(x.max()),
        "magnitude_step": float(step),
        "thresholds_used": int(len(x)),
        "catalogue_events": int(len(df)),
        "note": "Exploratory fit; interpretation depends on catalogue completeness and selected magnitude range."
    }
    return summary, x, y, pred, thresholds, counts


def make_figures(df, x, y, pred, thresholds, counts):
    RESULTS.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(9, 6))
    sc = ax.scatter(df["longitude"], df["latitude"], c=df["kmeans_cluster"], s=10, alpha=0.65)
    ax.set_title("Earthquake epicentres grouped by K-means")
    ax.set_xlabel("Longitude (degrees)")
    ax.set_ylabel("Latitude (degrees)")
    fig.colorbar(sc, ax=ax, label="K-means cluster")
    fig.tight_layout()
    fig.savefig(RESULTS / "earthquake_clusters.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(df["mag"], bins=20, edgecolor="black")
    ax.set_title("Earthquake magnitude distribution in selected catalogue")
    ax.set_xlabel("Magnitude")
    ax.set_ylabel("Number of events")
    fig.tight_layout()
    fig.savefig(RESULTS / "magnitude_distribution.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(x, y, label="Observed cumulative frequency")
    ax.plot(x, pred, label="Linear regression")
    ax.set_title("Gutenberg–Richter magnitude-frequency fit")
    ax.set_xlabel("Magnitude threshold m")
    ax.set_ylabel("log10(Number of events with magnitude ≥ m)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(RESULTS / "gutenberg_richter_curve.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    counts_df = pd.DataFrame({"magnitude_threshold": thresholds, "count_ge_threshold": counts})
    counts_df = counts_df[counts_df["count_ge_threshold"] > 0]
    ax.plot(counts_df["magnitude_threshold"], counts_df["count_ge_threshold"], marker="o")
    ax.set_yscale("log")
    ax.set_title("Cumulative earthquake count by magnitude threshold")
    ax.set_xlabel("Magnitude threshold")
    ax.set_ylabel("Number of events (log scale)")
    fig.tight_layout()
    fig.savefig(RESULTS / "cumulative_magnitude_frequency.png", dpi=180)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description="Himalayan earthquake clustering and Gutenberg–Richter analysis")
    parser.add_argument("--input", default="data/earthquakes.csv", help="Path to earthquake CSV")
    parser.add_argument("--clusters", type=int, default=4, help="Number of clusters (default: 4)")
    parser.add_argument("--bounds", nargs=4, type=float, default=[25, 38, 70, 100],
                        metavar=("MIN_LAT", "MAX_LAT", "MIN_LON", "MAX_LON"),
                        help="Geographic bounds; default 25 38 70 100")
    parser.add_argument("--min-mag", type=float, default=2.5, help="Minimum threshold for G-R curve")
    parser.add_argument("--max-mag", type=float, default=6.5, help="Maximum threshold for G-R curve")
    parser.add_argument("--mag-step", type=float, default=0.25, help="Magnitude threshold step")
    parser.add_argument("--hierarchical-max", type=int, default=2500,
                        help="Maximum records used in hierarchical clustering (O(n^2) memory)")
    args = parser.parse_args()

    if args.clusters < 2:
        parser.error("--clusters must be at least 2")
    input_path = Path(args.input)
    if not input_path.is_absolute():
        input_path = (ROOT / input_path).resolve()
    if not input_path.exists():
        raise FileNotFoundError(
            f"Input CSV not found: {input_path}\n"
            "Download/export a catalogue from https://earthquake.usgs.gov/earthquakes/search/ "
            "or https://seismo.gov.in/data-portal and save it as data/earthquakes.csv."
        )

    RESULTS.mkdir(parents=True, exist_ok=True)
    df, metadata = load_catalog(input_path, tuple(args.bounds))
    clustered, cluster_metrics, hier_n = cluster_catalog(df, args.clusters, args.hierarchical_max)
    clustered.to_csv(RESULTS / "cleaned_earthquakes.csv", index=False)
    cluster_metrics.to_csv(RESULTS / "cluster_metrics.csv", index=False)

    gr, x, y, pred, thresholds, counts = fit_gutenberg_richter(
        df, args.min_mag, args.max_mag, args.mag_step
    )
    with open(RESULTS / "gutenberg_richter_summary.json", "w", encoding="utf-8") as f:
        json.dump(gr, f, indent=2)
    make_figures(clustered, x, y, pred, thresholds, counts)

    summary = {
        **metadata,
        "student": "Prince",
        "roll_number": "24020570051",
        "assigned_problem_number": 59,
        "clusters_requested": args.clusters,
        "hierarchical_evaluated_samples": hier_n,
        "python_version": platform.python_version(),
        "pandas_version": pd.__version__,
        "numpy_version": np.__version__,
        "scikit_learn_version": sklearn.__version__,
        "scipy_version": scipy.__version__,
        "gutenberg_richter": gr,
        "interpretation_warning": "Exploratory regional analysis only; this model does not predict earthquakes or define official hazard zones."
    }
    with open(RESULTS / "analysis_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n=== Cluster metrics ===")
    print(cluster_metrics.to_string(index=False))
    print("\n=== Gutenberg–Richter fit ===")
    print(json.dumps(gr, indent=2))
    print(f"\nGenerated results and figures in: {RESULTS}")
    print("Use the actual generated values when writing the final paper; do not copy example metrics.")


if __name__ == "__main__":
    main()
