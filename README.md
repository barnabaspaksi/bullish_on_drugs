# Predictive Modeling of Regional GDP per Capita based on Wastewater-Based Epidemiology

## File organisation
 The project uses the following file-naming convention:
 - If there is a specific naming requirement in the assignment, it takes precedence over the following guidelines.
 - Unedited data retrieved from external sources are not renamed. Scripts referencing them may use descriptive names, rather than the original technical filenames. If they are preprocessed, the following schema should be used for the resulting files: [data_source]_[desc].[ext]. When there is more than one data source, use [desc].[ext].
 - All other filenames must use snake_case, separating all lowercased words clearly by underscores.
 - Special characters (incl. whitespaces, tabs, dots, parentheses) should be avoided. Note that using dots in R is permissible for variable names. 
 - Figures are named semantically, not just numbered.
 - Dates are given in ISO 8601 format (YYYY-MM-DD), i.e. months and days are padded. Dates appear after the description, before the version and extension.
 - Versioning should be avoided by using replacements and commits to Github, if possible. Otherwise, the version should not be padded (e.g. orchestrator_v4.py rather than orchestrator_v_4.py).
 - Scripts should not include the execution order. If necessary, an orchestrator should be provided.
 - Config files should have config_ prepended to them.
 - Documentation template: [document_type]_[subject]_[version].[ext]. Here, keeping documentation for older versions is permissible to minimize search time in commits and reflect the evolution of the project. Document types can include the following: model_card (Model Card), data_dict (Data Dictionary), report (Report).
 - Requirements for the environment should appear in requirements.txt for Python and renv.lock for R in the project root. Other files needed for running the analysis pipeline should be included in the project root.
 - The license should be at the project root. 
