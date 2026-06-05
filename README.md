# Predictive Modeling of Regional GDP based on Wastewater-Based Epidemiology

## 1. Install Dependencies
- Navigate to the docs folder in Terminal and run: conda env create -f environment.yml
- Open the file src/use-case-experiment-reproducible.R in RStudio (version 2026.05.0+218) using R version 4.6.0 and it should recommend installing all required packages. Note, if you do not see this recommendation, you can also look at the outputs/session_info.txt file which contains a full list of packages used during the experiment.
 
## 2. How to Execute the Experiment after Setup
- Two files are essential for this:
- 1. Obtain data from DBRepo using src/api_reimplementation.ipynb and save them locally (they do not need a lot of space).
- 2. Run the experiment and generate outputs using src/use-case-experiment-reproducible.R 
WARNING: the notebooks sometimes load for a long time when we keep reloading the RestClient stuff. This can be solved by restarting Python completely.

## File organisation
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

