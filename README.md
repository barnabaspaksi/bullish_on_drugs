# Predictive Modeling of Regional GDP based on Wastewater-Based Epidemiology

## 1. Install Dependencies
- Navigate to the docs folder in Terminal and run: conda env create -f environment.yml
- Open the file src/use-case-experiment-reproducible.R in RStudio (version 2026.05.0+218) using R version 4.6.0 and it should recommend installing all required packages.
 
## 2. How to Execute the Experiment after Setup
- Two files are essential for this:
- 1. Obtain data from DBRepo using src/api_reimplementation.ipynb and save them locally (they do not need a lot of space).
- 2. Run the experiment and generate outputs using src/use-case-experiment-reproducible.R 
WARNING: the notebooks sometimes load for a long time when we keep reloading the RestClient stuff. This can be solved by restarting Python completely.

## INFO FOR LAST DAY (PROGRESS):
I ran everything again and finished my part (T2.5):
step 0: derive_3NF creates the local files from the raw ones in the format which fits the schema. In particular, only rows which have a join partner may be uploaded.
step 1: create_db_dbrepo.py is run to create a new db. The id must be added to dotenv: DB_ID=5cde660e-153a-4bff-8e41-69e87cda399d
step 2: create_tables_dbrepo.ipynb is executed to initalize table schemas and basic type stuff (part of T2.1)
step 3: upload_metadata_dbrepo.ipynb adds licensing info and some metadata (end of T2.1)
step 4: semantic_mapping.ipynb can be run completely to add the concept_uri and unit_uri stuff to tables which are dedicated fields by default, not something we need to create as identifiers. (T2.2 and T2.3 are done together and complete)
step 5: create_views_dbrepo.ipynb is Amy's part but renamed and also running on the DB_ID from dotenv. It has the mistake of aggregations in objects which do not have that parameter, so these views are incorrect afaik (T2.4). Although I added currency as a column to gdp, it is not needed for analysis, so I left the views and only changed column names where necessary, for example daily_mean is not daily_mean_concentration.
step 6: upload_data_to_dbrepo.py is my solution for populating the tables with data. It works only when GDP is not an int, as those only allow numbers until 2 billion and some regions have higher GDPs. This is why I reran the entire pipeline documented here. (This concludes T2.5)

NEXT STEPS: use views to query the data in DBRepo and reproduce the experiment. Code for that is in use-case-experiment.R by Helene. I mostly implemented preprocessing until line 95 but there could be some tiny deviations, so I think comparing the view results with what is there after the joins would be a good idea.

## File organisation
 The project uses the following file-naming convention:
 - If there is a specific naming requirement in the assignment, it takes precedence over the following guidelines.
 - Unedited data retrieved from external sources are not renamed. Scripts referencing them may use descriptive names, rather than the original technical filenames. If they are preprocessed, the following schema should be used for the resulting files: [data_source]_[desc].[ext]. When there is more than one data source, use [desc].[ext].
 - All other filenames must use snake_case, separating all lowercased words clearly by underscores. Acronyms should be kept capitalized if customary.
 - Special characters (incl. whitespaces, tabs, dots, parentheses) should be avoided. Note that using dots in R is permissible for variable names. 
 - Figures are named semantically, not just numbered.
 - Dates are given in ISO 8601 format (YYYY-MM-DD), i.e. months and days are padded. Dates appear after the description, before the version and extension.
 - Versioning should be avoided by using replacements and commits to Github, if possible. Otherwise, the version should not be padded (e.g. orchestrator_v4.py rather than orchestrator_v_4.py).
 - Scripts should not include the execution order. If necessary, an orchestrator should be provided.
 - Config files should have config_ prepended to them.
 - Documentation template: [document_type]_[subject]_[version].[ext]. Here, keeping documentation for older versions is permissible to minimize search time in commits and reflect the evolution of the project. Document types can include the following: model_card (Model Card), data_dict (Data Dictionary), report (Report).
 - Requirements for the environment should appear in requirements.txt for Python and renv.lock for R in the project root. Other files needed for running the analysis pipeline should be included in the project root.
 - The license should be at the project root. 

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
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.20464727-blue)](https://doi.org/10.5281/zenodo.20464727)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.20464727.svg)](https://doi.org/10.5281/zenodo.20464727)
