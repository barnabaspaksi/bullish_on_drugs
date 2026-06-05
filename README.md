# Predictive Modeling of Regional GDP based on Wastewater-Based Epidemiology

## Abstract
This use case explores the correlation relationship between illicit drug use in major European cities and their regional economic productivity (GDP). 
<br> Original Publishers: 
<br> EUDA & SCORE: URI: https://www.euda.europa.eu/data/repository/drugs-municipal-wastewater-europe-source-data-2026_en 
<br> EUROSTAT: DOI: https://doi.org/10.2908/NAMA_10R_3GDP, URI: https://ec.europa.eu/eurostat/databrowser/view/nama_10r_3gdp__custom_20659344/default/table

## Methodology
Underlying Wastewater Data: 
<br> 1. Core Approach (Wastewater Analysis): The method analyzes communal wastewater for drugs and their metabolic products to estimate community-level drug consumption. It is a multi-disciplinary field combining analytical chemistry, physiology, sewage engineering, spatial epidemiology, and conventional drug epidemiology. 
<br> 2. Network & Timeframe: Data is collected by scientists and experts in a Europe-wide network called the Sewage analysis CORe group — Europe (SCORE). Data has been collected from a range of cities annually since 2011. <br> 3. Sampling & Measurement Specifics: 
<br> - Values reported: All values indicate the population-normalised loads of drug residues quantified in raw sewage. These values are not corrected with excretion factors. 
<br> - Multiple treatment plants: For cities with several sewage treatment plants (STPs), the data shows a population-weighted average (e.g., "Berlin (4)"). 
<br> - Quantification limits: Values below the method's limit of quantification are recorded as zero.
<br> - Daily averages: "Weekday means" are averages of samples from Tuesday, Wednesday, and Thursday. "Weekend means" are averages of Friday, Saturday, Sunday, and Monday. At least one sample is usually taken on each weekday.
<br> - Site information: A separate table in the original dataset published by EUDA and SCORE provides details on each treatment plant (SiteID, location, responsible institution, and approximate population served). 
<br> 4. Substance-specific Notes: The main excreted metabolite is measured for specific drugs (e.g., Benzoylecgonine for cocaine; THC-COOH for cannabis). City Mapping: Cities were manually mapped to relevant NUTS regions containing them. 

<br> GDP Data were retrieved from Eurostat, the main statistical authority responsible for collecting and provisioning economic data: 
<br> Source & Extraction: 
<br> Data Source: ESTAT (Eurostat) 
<br> Extraction Date: 23/03/2026 (11:48:35) 
<br> Last Update: 10/02/2026 (11:00) 
<br> Dataset Definition: Full Title: Gross domestic product (GDP) at current market prices by NUTS 3 region Dataset Code: nama_10r_3gdp__custom_20659344 
<br> Key Parameters (Dimensions): 
<br> Time Frequency: Annual 
<br> Unit of Measure: Million euro 
<br> Geographic Level: NUTS 3 regions (the finest regional level in Eurostat's NUTS classification) 
<br> Price Basis: Current market prices (not adjusted for inflation) 
<br> Time Period Covered: Years 
<br> Included: 2011 through 2024 (14 years) 
<br> Data uploaded to this dataset in DBRepo correspond to a subset of the original data, as we were required to transform them into third normal form (3NF).

<br> Data Stewardship and Preprocessing Challenge: While the drug dataset identifies locations by specific city strings (e.g., 'Graz', 'Steyr'), Eurostat utilizes standardized NUTS-3 administrative codes (e.g., 'DE212'). This is resolved via a custom mapping schema table ('city_map'). Only the active filtered subset utilized in this longitudinal frame is republished here.

<br> Temporal & Spatial Coverage: Annual wastewater tracking spans years 2011 to 2025 across 115 cities and 25 countries in the European Union, Norway, and Türkiye. GDP tracking spans annually from 2000 to 2024 across EU Member States, Candidate and potential Candidate Countries, Norway, and Switzerland. Our subset only contains common European countries for the years 2011-2024. Data availability varies across years and regions.

<br> Units of Measure: Wastewater metrics indicate concentrations (mg/1000p/day) of illicit drug loads (Cocaine, Methamphetamine, MDMA) measured from 24-hour composite samples collected over a single week between March and May. GDP values indicate economic output expressed in Euros at current market prices by NUTS 3 region.

## 1. Install Dependencies
- Navigate to the docs folder in Terminal and run: conda env create -f environment.yml
- Open the file src/use-case-experiment-reproducible.R in RStudio (version 2026.05.0+218) using R version 4.6.0 and it should recommend installing all required packages. Note, if you do not see this recommendation, you can also look at the outputs/session_info.txt file which contains a full list of packages used during the experiment.
 
## 2. How to Execute the Experiment after Setup
- Two files are essential for this:
- 1. Obtain data from DBRepo using src/api_reimplementation.ipynb and save them locally (they do not need a lot of space).
- 2. Run the experiment and generate outputs using src/use-case-experiment-reproducible.R 
WARNING: the notebooks sometimes load for a long time when we keep reloading the RestClient stuff. This can be solved by restarting Python completely.

## File organisation

```text
.
├── data/                   
│   ├── processed/           # data created by us 
│   └── raw/                 # original data from Eurostat and EUDA
├── docs/                    # Documentation and supplementary materials
├── outputs/                 # Generated artifacts from experiment
│   ├── metadata/            # FAIR4ML metadata and model cards
│   └── models/              # Trained models from R
├── schema/                  # Schemas for DBRepo 3NF Storage
├── src/                     # Source code 
├── CITATION.cff             # Citation metadata for the repository
├── LICENSE                  
├── README.md                # This file
├── codemeta.json            # Software metadata context
└── ro-crate-metadata.json   # RO-Crate research object description
```

 The project uses the following file-naming convention:
 - If there is a specific naming requirement in the assignment, it takes precedence over the following guidelines.
 - Unedited data retrieved from external sources are not renamed. Scripts referencing them may use descriptive names, rather than the original technical filenames. If they are preprocessed, the following schema should be used for the resulting files: [data_source]_[desc].[ext]. When there is more than one data source, use [desc].[ext].
 - All other filenames must use snake_case, separating all lowercased words clearly by underscores. Acronyms should be kept capitalized if customary.
 - Special characters (incl. whitespaces, tabs, dots, parentheses) should be avoided. Note that using dots in R is permissible for variable names. 
 - Figures are named semantically, not just numbered.
 - Dates are given in ISO 8601 format (YYYY-MM-DD), i.e. months and days are padded. Dates appear after the description, before the version and extension.
 - Versioning should be avoided by using replacements and commits to Github, if possible. Otherwise, the version should not be padded (e.g. orchestrator_v4.py rather than orchestrator_v_4.py).
 - Documentation: keeping documentation for older versions is permissible to minimize search time in commits and reflect the evolution of the project. 
 - Scripts should not include the execution order. If necessary, an orchestrator should be provided.
 - Config files should have config_ prepended to them.
 - The license should be at the project root. 

## Original Input Data
- data/raw/nama_10r_3gdp__custom_20659344_spreadsheet.csv (Eurostat GDP data)
- data/raw/ww2026-all-data_en.csv (Estimated concentrations of metabolites from illicit drugs in wastewater from EUDA & SCORE)
- data/processed/city_nuts_mapping_unique.csv (Manually compiled mapping from city names to NUTS-3 regions)

## Output Data
- The outputs folder contains visualizations generated before the experiment (exploratory analysis).
- The file outputs/model_metrics_comparison.csv contains the evaluation metrics from all models.
- The folder outputs/metadata containing fair4ml files along with model cards describe the machine learning models, their parameters, assumptions and expectations.
- The file outputs/session_info.txt serves as a pure unfiltered source of data regarding the run of the experiment to allow a perfect reproduction of the experimental environment. Workspace state logs are also provided before and after the analysis.
- Other outputs include data/processed which clearly document major steps in the process of obtaining the input data for the experiment from raw files (incl. DBRepo storage).

## Authors

- Barnabás Paksi (https://orcid.org/0009-0001-1032-0177)
- Helene Johanna Vaught (https://orcid.org/0009-0005-8421-9302)
- Vlada Hluschchenko (https://orcid.org/0009-0009-5136-9119)
- Amélie Assmayr (https://orcid.org/0009-0007-0543-4165)

The authors formed Group 20 in the course 194.045 Data Stewardship (UE 2,0) 2026S at TU Wien (https://ror.org/04d836q62).
    
## Licences

### Input Data
Both input datasets are licensed under CC BY 4.0:
- **EUDA** (wastewater data): source must be acknowledged as "EUDA and SCORE".
- **Eurostat** (GDP data): source must be acknowledged, changes must be indicated.

Reuse is permitted provided appropriate credit is given.

### Software / Code
MIT License — chosen for simplicity and full compatibility with the CC BY 4.0 
input data licence. See [LICENSE](./LICENSE).

### Output Data (models, figures, generated datasets)
Licensed under CC BY 4.0 — all outputs in the `outputs/` folder are freely 
reusable with attribution.

## Zenodo
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.20464726-blue)](https://doi.org/10.5281/zenodo.20464726)

