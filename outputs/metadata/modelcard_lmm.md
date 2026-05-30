---
# For reference on model card metadata, see the spec: https://github.com/huggingface/hub-docs/blob/main/modelcard.md?plain=1
# Doc / guide: https://huggingface.co/docs/hub/model-cards
editor_options: 
  markdown: 
    wrap: sentence
---

# Model Card for `lmm_model.rds`: Trained Nested Linear Mixed Model

<!-- Provide a quick summary of what the model is/does. -->

This model uses a Multiple Linear Regression to predict the regional GDP (by NUTS-3 region) based on wastewater metabolite concentrations of illicit drugs and longitudinal time data, utilizing the specific city region as a random effect to account for baseline economic differences.

## Model Details

### Model Description

This is a Multiple Linear Regression model developed in R using the base `lm()` function.
It was trained to explore a spurious correlation between the economic productivity of European cities (GDP by NUTS3) and their illicit drug consumption.
The model uses fixed effects for year, specific NUTS-3 region (`nuts_code`), and various drug metabolites (MDMA, amphetamine, cocaine, methamphetamine).

-   **Developed by:** Amélie Assmayr (ORCID: 0009-0007-0543-4165), Vlada Hlushchenko (ORCID: 0009-0009-5136-9119), Barnabás Paksi (ORCID: 0009-0005-8421-9302), Helene Vaught (ORCID: 0009-0009-5136-9119)
-   **Funded by [optional]:** N/A (Academic Data Stewardship Assignment)
-   **Model type:** Linear Regression
-   **Language(s) (NLP):** R
-   **License:** Creative Commons Attribution 4.0 International (CC-BY-4.0)

### Model Sources [optional]

<!-- Provide the basic links for the model. -->

-   **Repository:** <https://github.com/barnabaspaksi/bullish_on_drugs>

## Uses

<!-- Address questions around how the model is intended to be used, including the foreseeable users of the model and those affected by the model. -->

### Direct Use

<!-- This section is for the model use without fine-tuning or plugging into a larger ecosystem/app. -->

This model is intended strictly for educational purposes and academic data stewardship assignments.
It is designed to demonstrate reproducible experiments and document good practice in data stewardship rather than to uncover fundamental macroeconomic truths.
It can be used to reproduce the experiment of Group 20: Predictive Modeling of Regional GDP based on Wastewater-Based Epidemiology.

### Downstream Use [optional]

<!-- This section is for the model use when fine-tuned for a task, or when plugged into a larger ecosystem/app -->

N/A. This model is not intended to be plugged into broader economic forecasting ecosystems.

### Out-of-Scope Use

<!-- This section addresses misuse, malicious use, and uses that the model will not work well for. -->

This model is unfit for actual economic forecasting or municipal policy-making.
It must not be used for law enforcement resource allocation, urban planning, or public health interventions.
The relationship modeled is assumed to be coincidental or spurious; users must remember that correlation does not imply causation.

## Bias, Risks, and Limitations

<!-- This section is meant to convey both technical and sociotechnical limitations. -->

**Technical Limitations:** A significant technical limitation is that the model performs suspiciously well, which is highly likely due to the inclusion of the city (`nuts_code`) variable acting as a random effect.
Instead of learning a genuine relationship between illicit drugs and GDP, the model is likely just memorizing the baseline GDP of specific regions through its random intercept.
Future iterations of this experiment could remove the city variable entirely to evaluate the true predictive power of the wastewater metabolites alone.
Furthermore, this simple linear model lacks regularization (making it highly susceptible to multicollinearity among drug metabolites), assumes an independence of observations that is violated by cities with multiple sewage plants, and relies on OLS assumptions where outliers can have disproportionate influence on coefficients.
It may also miss non-linear patterns entirely.

**Ethical Considerations:** Associating illicit drug use with economic output carries a substantial ethical risk of stigmatizing specific cities, regions, or vulnerable populations.
There is a danger that non-experts might misinterpret these spurious predictions as a genuine endorsement of substance abuse for economic productivity.
Care must be taken to clearly communicate the humorous and purely educational intent behind this data stewardship exercise.

### Recommendations

<!-- This section is meant to convey recommendations with respect to the bias, risk, and technical limitations. -->

Users (both direct and downstream) should be made aware of the risks, biases, and limitations of the model.
When reusing this model contextual framing is important.
Any repository or generated reports should prominently feature a disclaimer regarding the spurious nature of the correlation being explored.

## How to Get Started with the Model

Use the code below to get started with the model.

``` r
# load singular model 
saved_model <- readRDS("../outputs/models/lmm_model.rds")

# load all models
load("../outputs/models/all_models.RData") # rf_fit, mlr_nested, and lmm_model
```

## Training Details

### Training Data

<!-- This should link to a Dataset Card, perhaps with a short stub of information on what the training data is all about as well as documentation related to data pre-processing or additional filtering. -->

The model was trained on a merged longitudinal dataset combining two primary open-source databases.
The economic baseline is provided by EUROSTAT GDP metrics at current market prices by NUTS-3 regions (DOI: 10.2908/NAMA_10R_3GDP).
The drug metabolite data originates from the EUDA (and SCORE) "Drugs in municipal wastewater in Europe: Source data 2026" (<https://www.euda.europa.eu/data/repository/drugs-municipal-wastewater-europe-source-data-2026_en> (Accessed: March 23, 2026)).
The finalized, cleaned dataset representing the merged data is published under the TU Vienna DBRepo (DOI: 10.82556/pbwe-bk06).

### Training Procedure

<!-- This relates heavily to the Technical Specifications. Content here should link to that section when it is relevant to the training procedure. -->

#### Preprocessing [optional]

Data was filtered to include only valid 5-character NUTS-3 codes and aggregated into wide format.
Column names, city names, and metabolite values were explicitly lowercased.
Due to a lack of shared identifiers, a mapping schema (city_nuts_mapping_unique.csv) was utilized to link EUDA city strings to Eurostat NUTS-3 administrative codes.
Variables with excessive missing data (cannabis, ketamine, cot, ets) were dropped, and missing rows were removed via listwise deletion.
The remaining dataset was split into an 80/20 train-test split utilizing a set seed (123) for reproducibility, yielding 409 training observations and 97 test observations spanning 102 geographic groups.

#### Training Hyperparameters

-   **Algorithm:** Multiple Linear Regression (Base R `stats::lm()`)
-   **Method:** Ordinary Least Squares (OLS)
-   **Formula:** `gdp ~ ref_year + mdma + amphetamine + cocaine + methamphetamine + nuts_code`
-   **Intercept:** True
-   **NA Action:** `na.omit`

#### Speeds, Sizes, Times [optional]

<!-- This section provides information about throughput, start/end time, checkpoint size if relevant, etc. -->

{{ speeds_sizes_times \| default("[More Information Needed]", true)}}

## Evaluation

<!-- This section describes the evaluation protocols and provides the results. -->

### Testing Data, Factors & Metrics

#### Testing Data

<!-- This should link to a Dataset Card if possible. -->

The evaluation utilized a 20% holdout test dataset generated during the preprocessing phase via random sampling.

#### Factors

<!-- These are the things the evaluation is disaggregating by, e.g., subpopulations or domains. -->

The evaluation incorporates the nuts_code as a grouping factor to allow the model to handle new levels or variations at the regional geographic layer.

#### Metrics

<!-- These are the evaluation metrics being used, ideally with a description of why. -->

Standard regression performance metrics were computed using the yardstick R package: Root Mean Squared Error (RMSE), Mean Absolute Error (MAE), and R-Squared (RSQ).

### Results

The evaluation of this regression model utilized a 20% holdout test dataset.
To assess predictive accuracy for the continuous GDP variable, the standard regression metrics Root Mean Squared Error (RMSE), Mean Absolute Error (MAE), and R-Squared were computed.
The Simple Linear Regression performed reasonably well, significantly outperforming the Random Forest, though it was marginally beaten by the Nested LMM.

| Model             | RMSE               | R-Squared (RSQ)    | MAE                |
|------------------|------------------|------------------|------------------|
| **Random Forest** | 31249340027.013645 | 0.7296339449080923 | 22073943574.487278 |
| **Simple Linear** | 6272378553.334199  | 0.9895954049265466 | 4554543320.30225   |
| **Nested Linear** | 6208319190.0452385 | 0.9894390254627119 | 4488942285.003483  |

#### Summary

The evaluation reveals that the Simple Linear Regression model performed significantly better than the Random Forest architecture.
However, its performance was marginally lower than the Nested LMM, which is able to represent the hierarchical reality of the data better by treating regions as random effects instead of fixed effects.

## Model Examination [optional]

<!-- Relevant interpretability work for the model goes here -->

{{ model_examination \| default("[More Information Needed]", true)}}

## Environmental Impact

<!-- Total emissions (in grams of CO2eq) and additional considerations, such as electricity usage, go here. Edit the suggested text below accordingly -->

Carbon emissions can be estimated using the [Machine Learning Impact calculator](https://mlco2.github.io/impact#compute) presented in [Lacoste et al. (2019)](https://arxiv.org/abs/1910.09700).

-   **Hardware Type:** CPU
-   **Hours used:** \<1 hour
-   **Cloud Provider:** Local Execution
-   **Compute Region:** Austria
-   **Carbon Emitted:** {{ co2_emitted \| default("[More Information Needed]", true)}}

## Technical Specifications [optional]

### Model Architecture and Objective

Multiple Linear Regression architecture utilizing Ordinary Least Squares (OLS) to model the linear relationship between the continuous regional GDP target and multiple fixed-effect predictors, including time, specific regional municipal geography, and metabolic concentrations.

### Compute Infrastructure

Standard local R environment.

#### Hardware

{{ hardware_requirements \| default("[More Information Needed]", true)}}

#### Software

-   **R Version:** 4.6.0 (2026-04-24 ucrt)
-   **Key Dependencies:** `tidymodels_1.5.0`, `tidyverse_2.0.0`

## Citation [optional]

<!-- If there is a paper or blog post introducing the model, the APA and Bibtex information for that should go in this section. -->

**BibTeX:**

{{ citation_bibtex \| default("[More Information Needed]", true)}}

**APA:**

{{ citation_apa \| default("[More Information Needed]", true)}}

## Glossary [optional]

<!-- If relevant, include terms and calculations in this section that can help readers understand the model or model card. -->

{{ glossary \| default("[More Information Needed]", true)}}

## More Information [optional]

License: The model weights, accompanying code, and processed datasets are distributed openly.
They are explicitly licensed under the Creative Commons Attribution 4.0 International (CC-BY-4.0) license.

Machine readable FAIR4ML metadata can be found on the repository as well.

## Model Card Authors [optional]

{{ model_card_authors \| default("[More Information Needed]", true)}}

## Model Card Contact

Amélie Assmayr (ORCID: 0009-0007-0543-4165), Vlada Hlushchenko (ORCID: 0009-0009-5136-9119), Barnabás Paksi (ORCID: 0009-0005-8421-9302), Helene Vaught (ORCID: 0009-0009-5136-9119)
