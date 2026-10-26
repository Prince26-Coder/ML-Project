# Spatio-temporal Clustering of Earthquakes in the Himalayan Region

**Student:** Prince  
**University Roll No.:** 24020570051  
**Problem No.:** 59  
**Domain:** Disaster Management  
**SDGs:** SDG 11 – Sustainable Cities and Communities; SDG 9 – Industry, Innovation and Infrastructure  
**Article Type:** Regional Hazard Case Study

## Abstract

The Himalayan region is seismically active, making the analysis of earthquake distributions relevant to disaster-risk research. This project applies machine-learning techniques to explore earthquake epicentres and magnitude-frequency patterns in a selected Himalayan and northeastern Indian study region. K-means clustering and agglomerative hierarchical clustering were used to group earthquake events, while linear regression was applied to the Gutenberg–Richter magnitude-frequency relationship. The K-means model produced four clusters with a silhouette score of 0.3881. Hierarchical clustering also produced four clusters, with a reported silhouette score of 0.3768. The Gutenberg–Richter regression yielded an estimated b-value of 0.8253 and an R² of 0.9505. The spatial plots indicate non-uniform distributions of recorded epicentres, while the magnitude histogram shows fewer recorded events at higher magnitudes. These results demonstrate the usefulness of clustering and regression for exploratory seismicity analysis. The findings are not earthquake predictions or official seismic-hazard classifications.

**Keywords:** Earthquake catalogue, Himalaya, spatial clustering, K-means, hierarchical clustering, haversine distance, Gutenberg–Richter relationship, disaster management.

## 1. Introduction

The Himalayan region experiences significant seismic activity associated with the ongoing convergence of the Indian and Eurasian tectonic plates. Understanding the distribution of earthquake epicentres and the frequency of different earthquake magnitudes is important for regional seismicity research and disaster-management planning.

Machine-learning methods can help identify patterns in earthquake catalogues. Clustering groups observations according to similarities in their features, while regression can quantify relationships between magnitude and cumulative earthquake frequency.

This project investigates spatial groupings in a selected earthquake catalogue using K-means and agglomerative hierarchical clustering. It also examines the Gutenberg–Richter magnitude-frequency relationship through linear regression.

The principal objectives are to identify exploratory spatial patterns, evaluate cluster separation using silhouette scores, estimate the magnitude-frequency relationship, and discuss the limitations of applying these methods to earthquake data.

## 2. Related Work

Research has examined the spatial distribution of seismicity and variations in earthquake magnitude-frequency relationships across the Himalayan region.

Kumar and Sharma (2019) studied the seismicity of the central and northeastern Himalayan region using the Gutenberg–Richter relationship. Their work highlights spatial heterogeneity in seismicity and the importance of examining regional earthquake patterns.

Chingtham et al. (2014) assessed seismicity parameters in the northwest Himalaya and adjoining regions, including the magnitude of completeness and the Gutenberg–Richter parameters. Their findings illustrate why catalogue quality and regional differences matter when interpreting seismicity statistics.

Gutenberg and Richter (1944) established the frequency-magnitude relationship widely used in earthquake research. In its common form, the relationship describes a linear trend between earthquake magnitude and the logarithm of cumulative event frequency.

The present project uses these ideas for an educational, exploratory analysis. Unlike detailed seismological studies, it does not establish geological fault relationships, estimate official hazard levels, or forecast individual earthquakes.

## 3. Dataset and Preprocessing

The project uses an earthquake catalogue stored as `data/earthquakes.csv`. The National Center for Seismology (NCS) Data Portal was identified as the primary data source in the project allocation, with the USGS Earthquake Catalog listed as an alternative.

**Data-source verification:** The exact catalogue source, download date, observation period, and query filters should be confirmed from the downloaded file and the original catalogue query before final submission.

The required variables include event time, latitude, longitude, depth, and magnitude. These attributes allow the project to examine where earthquakes occurred, their recorded depths, and their reported magnitudes.

The preprocessing script handles recognised column-name variations, parses event timestamps, and removes records with invalid coordinates or missing required values. The study region is defined in the code using geographic bounds; the configured bounds should be reported alongside the actual summary generated by the script.

The regression output reports 6,009 events. This count should be interpreted according to the precise dataset and filtering stage represented in the program output. The cleaned row count, date range, original row count, and other filtering details should be taken from `results/analysis_summary.json`.

Catalogue completeness is an important limitation. Smaller earthquakes may be missing because of detection and reporting differences. Consequently, the catalogue may not represent every earthquake that occurred during the study period.

## 4. Methodology

### 4.1 K-means Clustering

K-means is an unsupervised-learning algorithm that divides observations into a predefined number of clusters. It iteratively assigns observations to cluster centres and updates those centres to reduce within-cluster squared distances.

In this project, K-means was configured to produce four clusters using standardised latitude, longitude, depth, and magnitude features. Standardisation helps prevent features with larger numerical scales from dominating the distance calculations.

The resulting visualisation displays earthquake epicentres by cluster. Since the algorithm operates on standardised features and uses Euclidean distance, its treatment of geographic coordinates is an approximation rather than a direct measurement of distance over the Earth's surface.

### 4.2 Agglomerative Hierarchical Clustering

Agglomerative hierarchical clustering begins with individual observations and progressively merges groups according to a distance criterion.

The project applies haversine distance to earthquake epicentres for hierarchical clustering. Haversine distance accounts for the Earth's curvature and is more appropriate than ordinary Euclidean distance for measuring geographic separation using latitude and longitude.

The hierarchical method also produces four clusters. Because distance calculations can become computationally expensive for large catalogues, the implementation may use a subset of observations. The exact sample size should be confirmed from the code or output before reporting it.

The two clustering approaches use different feature and distance definitions. Their silhouette scores therefore should not be treated as a perfectly controlled, direct comparison.

### 4.3 Cluster Evaluation

The silhouette score evaluates how similar an observation is to its assigned cluster compared with other clusters. It ranges from −1 to 1. Higher values generally indicate more clearly separated clusters, while values near zero indicate overlapping groups.

The reported scores are 0.3881 for K-means and 0.3768 for hierarchical clustering. These values suggest some cluster structure, but separation is moderate rather than exceptionally strong.

A silhouette score measures cluster structure; it does not measure earthquake prediction accuracy or seismic hazard.

### 4.4 Gutenberg–Richter Regression

The Gutenberg–Richter relationship describes the cumulative frequency of earthquakes above a magnitude threshold. It is commonly expressed as:

\[
\log_{10}N(M\geq m)=a-bm
\]

where \(N(M\geq m)\) represents the number of recorded earthquakes with magnitude at least \(m\), \(a\) is the intercept, and \(b\) is the magnitude-frequency slope parameter.

The project calculates cumulative event frequencies over magnitude thresholds and fits a linear regression to their base-10 logarithms. The regression output reports a magnitude range of 2.5–6.5, an intercept of 6.3024, a slope of −0.8253, and an R² of 0.9505.

The b-value is estimated as the negative of the fitted slope, giving 0.8253. Its interpretation depends on catalogue completeness, magnitude consistency, the observation period, and the chosen fitting range.

## 5. Experimental Setup

The analysis was executed using Python 3.13.16. The project dependencies were installed through `requirements.txt`, and the analysis was launched using:

`python src/run_analysis.py`

The experiment used four clusters for both clustering approaches. K-means used standardised latitude, longitude, depth, and magnitude, while hierarchical clustering used geographic haversine distance.

The regression examined magnitude thresholds from 2.5 to 6.5. The analysis generated visualisations and summary files in the `results` directory.

For reproducibility, the final project record should include the catalogue source and download date, geographic bounds, observation period, preprocessing counts, hierarchical sample size, and relevant library versions.

## 6. Results

### 6.1 Spatial Clustering

K-means produced four clusters and a silhouette score of 0.3881. Hierarchical clustering also produced four clusters, with a reported silhouette score of 0.3768.

The generated cluster visualisation shows that earthquake epicentres are not distributed uniformly across the plotted region. Some portions of the map contain concentrated groupings, while others contain more dispersed observations. A cluster extending across a broad area also overlaps geographically with other groups.

These visual patterns indicate statistical groupings within the selected catalogue. They do not establish that each cluster corresponds to a separate geological fault, tectonic unit, or official seismic zone.

### 6.2 Magnitude Distribution

The magnitude histogram shows a concentration of recorded events around magnitude 4, with many observations approximately between magnitudes 2.5 and 4.5. The frequency declines at higher magnitudes, with comparatively few recorded events above magnitude 6.

This pattern is consistent with the general observation that smaller earthquakes are more frequent than larger earthquakes. However, the observed distribution can be influenced by catalogue coverage and the completeness of magnitude reporting.

### 6.3 Gutenberg–Richter Regression

The fitted regression equation is:

\[
\log_{10}N(M\geq m)=6.3024-0.8253m
\]

The estimated b-value is 0.8253, and the regression R² is 0.9505. The R² indicates a strong linear association between the magnitude thresholds and log cumulative frequencies used in the fitted regression. It does not mean the model predicts earthquakes with 95.05% accuracy.

Some deviations between the observed points and fitted line remain visible. The estimated b-value should therefore be treated as an exploratory result rather than a definitive regional seismic parameter.

### 6.4 Figures

Include the following generated figures in the final report:

1. **Earthquake clusters:** `results/earthquake_clusters.png`
2. **Magnitude distribution:** `results/magnitude_distribution.png`
3. **Gutenberg–Richter curve:** `results/gutenberg_richter_curve.png`

The figures should be inserted with numbered captions and referred to in the discussion.

## 7. Discussion

The clustering results show that unsupervised learning can be used to explore spatial structure in an earthquake catalogue. K-means achieved a silhouette score of 0.3881, while hierarchical clustering achieved 0.3768. Although the K-means score is numerically higher, the different distance definitions and feature spaces mean that this difference alone does not establish that K-means is the better method.

The cluster visualisation indicates non-uniform epicentre distributions. This can motivate further analysis of regional seismicity, but geological interpretation would require comparison with fault maps, tectonic information, and published seismic studies.

The magnitude histogram shows declining event frequencies at higher magnitudes. The regression similarly quantifies a negative relationship between magnitude threshold and log cumulative frequency. The high R² describes the fitted observations but does not establish catalogue completeness or guarantee that the fitted relationship will remain valid outside the selected data range.

For disaster-management applications, these techniques may support exploratory summaries and research prioritisation. They should not be used independently to assign official hazard levels or make operational earthquake forecasts.

## 8. Limitations and Future Work

Several limitations should be considered.

First, earthquake catalogues may contain missing events, inconsistent magnitude scales, and variations in detection capability. Catalogue completeness should be assessed before interpreting the b-value as a regional seismological parameter.

Second, the clustering results depend on feature selection, standardisation, the chosen cluster count, and distance definitions. The use of different feature spaces also limits direct comparison of the silhouette scores.

Third, hierarchical clustering can require substantial computation for large datasets, and sampling may affect its results. The robustness of the clusters should be assessed by testing alternative cluster counts and sampling strategies.

Fourth, the analysis does not establish causal geological relationships or predict the timing and location of future earthquakes.

Future work could include sensitivity analysis, catalogue-completeness assessment, comparison with established seismic zones, examination of depth and magnitude distributions within each cluster, and more detailed temporal analysis.

## 9. Conclusion

This project applied K-means clustering, agglomerative hierarchical clustering, and Gutenberg–Richter linear regression to explore earthquake patterns in a selected Himalayan-region catalogue.

K-means produced four clusters with a silhouette score of 0.3881, while hierarchical clustering produced four clusters with a reported score of 0.3768. The magnitude-frequency regression yielded an estimated b-value of 0.8253 and an R² of 0.9505.

The visualisations suggest a non-uniform spatial distribution of recorded epicentres and declining event frequencies at higher magnitudes. These results demonstrate how classical machine-learning methods can support exploratory analysis of earthquake catalogues. Further validation, catalogue-completeness assessment, and geological interpretation would be required before drawing stronger conclusions about regional seismicity or hazard.

## Declarations

**Data availability:** The project catalogue is stored in `data/earthquakes.csv`. The exact source, query settings, and download date must be verified against the original downloaded catalogue.

**Code availability:** The analysis code is included in the project's GitHub repository.

**Conflict of interest:** The author should declare any actual conflicts of interest, or state that there are none if that is accurate.

**Use of AI tools:** AI assistance was used for report drafting and explanation. The final disclosure should follow the university's academic-integrity policy.

## References

1. National Center for Seismology, Ministry of Earth Sciences, Government of India. *Data Portal*. https://seismo.gov.in/data-portal

2. U.S. Geological Survey. *Earthquake Catalog*. https://earthquake.usgs.gov/earthquakes/search/

3. Gutenberg, B., & Richter, C. F. (1944). Frequency of earthquakes in California. *Bulletin of the Seismological Society of America, 34*(4), 185–188.

4. Kumar, S., & Sharma, N. (2019). The seismicity of central and north-east Himalayan region. *Contributions to Geophysics and Geodesy, 49*(3), 265–281. https://doi.org/10.2478/congeo-2019-0014

5. Chingtham, P., Chopra, S., Baskoutas, I., & Bansal, B. (2014). An assessment of seismicity parameters in northwest Himalaya and adjoining regions. *Natural Hazards, 71*, 1599–1616.
