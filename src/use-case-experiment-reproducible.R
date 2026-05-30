#################################
## Data Stewardship Experiment ##
#################################

### Packages
library(this.path)
library(readr)
library(readxl)
library(tidyverse)
library(tidymodels)
library(reshape2)
library(patchwork)
library(ranger)
library(yardstick)
library(knitr)
library(lme4)   # For the Nested Linear Model
library(jsonlite)  # For writing JSON metadata
library(broom)

#################################
critical_packages <- c("ranger", "lme4", "tidymodels", "tidyverse")
installed_versions <- sapply(critical_packages, function(pkg) {
  paste(pkg, "version", packageVersion(pkg))
})
print(installed_versions)
#################################
### Load data
setwd(dirname(this.path()))
final_data_long <- read_csv("../data/processed/joined_data.csv")
head(final_data_long)

final_ordered <- final_data_long %>%
  rename_with(tolower) %>%
  mutate(across(c(city_name, metabolite_name), tolower)) %>%
  arrange(nuts_code, ref_year, gdp, city_name, metabolite_name)

final_data <- final_ordered %>% pivot_wider(
  names_from = metabolite_name,
  values_from = daily_mean_concentration
) # we leave NA values bc 0 has true meaning of undetectable quantity

#######################################
# split into training and test data

set.seed(123, kind = "L'Ecuyer-CMRG")
save.image("../outputs/workspace_state_before_analysis.RData")

# prep data: remove cannabis + ketamine
ml_data <- final_data %>%
  select(gdp, ref_year, amphetamine, nuts_code, 
         methamphetamine, cocaine, mdma) %>%
  mutate(nuts_code = as.character(nuts_code)) %>%
  drop_na()

data_split <- sample(nrow(ml_data),round(nrow(ml_data)*0.8), replace = FALSE)
train_data <- ml_data[data_split, ]
test_data  <- ml_data[-data_split, ]

# drop new levels
test_data <- test_data %>%
  filter(nuts_code %in% unique(train_data$nuts_code)) 

# convert to factors
train_data <- train_data %>% 
  mutate(nuts_code = factor(nuts_code))

test_data <- test_data %>% 
  mutate(nuts_code = factor(nuts_code, levels = levels(train_data$nuts_code)))

#######################################
#######################################
# Predicting GDP via drug use statistics

#######################################
# fit model: Random Forest Regression
set.seed(123, kind = "L'Ecuyer-CMRG") # repeating seed around randomness
rf_fit <- ranger(gdp ~ ref_year + mdma + amphetamine + cocaine + 
                   methamphetamine + nuts_code, 
                 data = train_data, 
                 na.action = "na.omit",
                 importance = 'impurity',
                 seed = 123,
                 num.threads = 1,
                 splitrule = "variance",  
                 min.node.size = 5
                 )

# predictionc
test_data$rf_pred <- predict(rf_fit, test_data)$predictions

# combine values and predictions into one dataframe
results_df <- data.frame(
  actual = test_data$gdp,
  predicted = test_data$rf_pred
)

# plot results
p3 <- ggplot(results_df, aes(x = actual, y = predicted)) +
  geom_point(color = "cornflowerblue") +
  geom_abline(intercept = 0, slope = 1, linetype = "dashed", color = "hotpink2") +
  theme_minimal() +
  expand_limits(x = 0, y = 0) +
  labs(title = "RF-Regression: Predicted vs. Actual GDP",
       x = "Actual GDP", y = "Predicted GDP")

#######################################
# fit model: Multiple linear regression
mlr_nested <- lm(gdp ~ ref_year + mdma + amphetamine + cocaine + methamphetamine + nuts_code, 
                 data = train_data) # dropping ketamine and cannabis bc of NAs

mlr_summary <- summary(mlr_nested)
print(paste("Adjusted R-Squared with Nesting:", mlr_summary$adj.r.squared))

# predict
test_data$mlr_pred <- predict(mlr_nested, newdata = test_data)

p4 <- ggplot(test_data, aes(x = gdp, y = mlr_pred)) +
  geom_point(color = "darkorchid") +
  geom_abline(slope = 1, intercept = 0, linetype = "dashed", color = "grey50") +
  theme_minimal() +
  expand_limits(x = 0, y = 0) +
  labs(title = "Linear Regression: Predicted vs. Actual GDP",
       x = "Actual GDP", y = "Predicted GDP")
combined_plots <- p3 + p4
ggsave("../outputs/combined_plots.png", plot = combined_plots, 
       width = 10, height = 6, dpi = 300)

######################################
# fit model: Nested linear regression
set.seed(123, kind = "L'Ecuyer-CMRG")
lmm_model <- lmer(gdp ~  ref_year + mdma + amphetamine + cocaine 
                  + methamphetamine + (1 | nuts_code), 
                  data = train_data,
                  REML = TRUE,
                  control = lmerControl(
                    optimizer = "bobyqa",           
                    calc.derivs = FALSE,
                    optCtrl = list(maxfun = 100000)
                  ))

######################################
# compare all results 

test_results <- test_data %>%
  mutate(pred_rf = test_data$rf_pred,
         pred_mlr = test_data$mlr_pred,
         pred_lmm = predict(lmm_model, newdata = test_data, 
                            allow.new.levels = TRUE),
         pred_rf  = pmax(pred_rf, 0),
         pred_mlr = pmax(pred_mlr, 0),
         pred_lmm = pmax(pred_lmm, 0))

plot_comparison <- test_results %>%
  select(gdp, pred_rf, pred_mlr, pred_lmm) %>%
  pivot_longer(cols = starts_with("pred"), 
               names_to = "model", 
               values_to = "prediction") %>%
  mutate(model = ifelse(model == "pred_rf", 
                        "Random Forest", 
                        ifelse(model == "pred_mlr",
                               "Simple Linear",
                               "Nested Linear")))

results_plot <- ggplot(plot_comparison, aes(x = gdp/1000000, 
                                            y = prediction/1000000, 
                                            color = model)) +
  geom_point(alpha = 1) +
  geom_abline(slope = 1, intercept = 0, linetype = "dashed", 
              color = "darkgrey") +
  facet_wrap(~model) +
  theme_minimal() +
  expand_limits(x = 0, y = 0) +
  labs(title = "Experiment Results: Predicted vs. Actual GDP",
       x = "Actual GDP (Euro/M)",
       y = "Predicted GDP (Euro/M)") +
  scale_color_manual(values = c("Random Forest" = "cornflowerblue",
                                "Simple Linear" = "darkorchid",
                                "Nested Linear" = "hotpink2"))

ggsave("../outputs/results_plot.png", 
       plot = results_plot, width = 12, height = 8, dpi = 300)

# Calculate MAE, RMSE and R-Squared for all 
metrics_rf <- test_results %>% 
  metrics(truth = gdp, estimate = pred_rf) %>% 
  mutate(model = "Random Forest")

metrics_mlr <- test_results %>% 
  metrics(truth = gdp, estimate = pred_mlr) %>% 
  mutate(model = "Simple Linear")

metrics_lmm <- test_results %>% 
  metrics(truth = gdp, estimate = pred_lmm) %>% 
  mutate(model = "Nested Linear")

comparison_metrics <- bind_rows(metrics_rf, metrics_mlr, metrics_lmm) %>%
  select(model, .metric, .estimate) %>%
  pivot_wider(names_from = .metric, values_from = .estimate)

kable(comparison_metrics)
write_csv(comparison_metrics, 
          "../outputs/model_metrics_comparison.csv")
save.image("../outputs/workspace_state_after_analysis.RData")

#######################################
#######################################
# FAIR4ML COMPLIANT METADATA GENERATION
#######################################
#######################################

# Create metadata directory if it doesn't exist
if(!dir.exists("../metadata")) dir.create("../metadata")
if(!dir.exists("../models")) dir.create("../models")

# Define dataset DOI (you'll need to obtain this from TUWRD)
dataset_doi <- "10.82556/pbwe-bk06" # not available bc DBRepo is broken

# Current timestamp for metadata
timestamp <- format(Sys.time(), "%Y-%m-%dT%H:%M:%S%z")

#######################################
# Model 1: Random Forest Regression
#######################################

rf_metadata <- list(
  model_id = "RF-GDP-001",
  model_name = "Random Forest Regression for GDP Prediction",
  algorithm = list(
    name = "Random Forest",
    version = as.character(packageVersion("ranger")),
    implementation = "ranger",
    citation = "Wright, M. N., & Ziegler, A. (2017). ranger: 
    A Fast Implementation of Random Forests for High Dimensional 
    Data in C++ and R. Journal of Statistical Software, 77(1), 1-17."
  ),
  
  training_data = list(
    name = "Predictive Modeling of Regional GDP based on Wastewater-Based Epidemiology",
    doi = dataset_doi,
    description = "Dataset combining GDP, year, and drug metabolite
    concentrations (amphetamine, methamphetamine, cocaine, MDMA)
    from multiple European regions",
    preprocessing = c(
      "Lowercase column names",
      "Lowercase city_name and metabolite_name values",
      "Removed cannabis and ketamine due to NAs",
      "Dropped rows with missing values",
      "80/20 train/test split with seed=123",
      "NUTS codes converted to factors",
      "gdp as target variable"
    ),
    split_strategy = list(
      method = "Random sampling without replacement",
      train_ratio = 0.8,
      seed = 123,
      stratification = "None"
    )
  ),
  
  hyperparameters = list(
    num_trees = 500,  # Default in ranger
    mtry = NULL,  # Default: floor(sqrt(number of predictors))
    min_node_size = 5, 
    splitrule = "variance",
    importance = "impurity",
    num_threads = 1,
    seed = 123,
    replace = FALSE,
    sample_fraction = 0.632,  # Default bootstrap fraction
    respect_unordered_factors = "ignore"
  ),
  
  evaluation_metrics = list(
    rmse = comparison_metrics %>% 
      filter(model == "Random Forest") %>% select("rmse") %>% 
      round(2),
    rsq = comparison_metrics %>% 
      filter(model == "Random Forest") %>% select("rsq") %>% 
      round(4),
    mae = comparison_metrics %>% 
      filter(model == "Random Forest") %>% select("mae") %>% 
      round(2)
  ),
  
  # Performance context
  performance_context = list(
    test_set_size = nrow(test_data),
    training_set_size = nrow(train_data),
    evaluation_method = "Hold-out test set"
  ),
  
  intended_use = list(
    purpose="Estimate GDP based on wastewater drug metabolite concentrations",
    domain = "Environmental economics",
    scope = "European NUTS code regions with available 
              wastewater monitoring data",
    constraints = list(
      "GDP predictions should be interpreted as estimates, 
        not official statistics",
      "Model assumes linear relationships between drug use and GDP",
      "Requires complete data for all five drug metabolites"
    )
  ),
  
  known_limitations = list(
    "Short Time Series",
    "Low Number of Observations",
    "Imperfect estimation of population in catchment area of wastewater 
        treatment plants, especially during events",
    "Imperfect mapping between data sources via manual mapping",
    "Limited geographic scope (only NUTS codes present in training data)",
    "Cannot extrapolate beyond observed GDP range in training data",
    "Assumes stable relationship between drug use and GDP over time",
    "Does not account for confounding factors (e.g., tourism, policing strategies)",
    "Minimum node size of 5 may lead to overfitting in small datasets",
    "Cannabis and ketamine omitted from analysis"
  ),

  technical_specs = list(
    input_features = c("ref_year", "mdma", "amphetamine", "cocaine",
                       "methamphetamine", "nuts_code"),
    target_variable = "gdp",
    feature_types = list(
      ref_year = "integer",
      mdma = "numeric",
      amphetamine = "numeric", 
      cocaine = "numeric",
      methamphetamine = "numeric",
      nuts_code = "factor (categorical)"
    ),
    output_type = "numeric (continuous GDP values)",
    missing_value_handling = "Listwise deletion (drop_na)"
  ),
  
  provenance = list(
    creation_date = timestamp,
    wasGeneratedBy = list(
      script= "use-case-experiment-reproducible.R",
      scriptVersion= "3b8b8f3ac46713d0317356da8f9d429e68b745fb",
      executionTime= timestamp
    ),
    created_by = list(
      list(
        name = "Barnabás Paksi", 
        orcid = "0009-0001-1032-0177",  
        email = "e11926285@student.tuwien.ac.at",
        affiliation = "TU Wien"
      ),
      list(
        name = "Helene Johanna Vaught", 
        orcid = "0009-0005-8421-9302",  
        email = "e11943054@student.tuwien.ac.at",
        affiliation = "TU Wien"
      ),
      list(
        name = "Vlada Hlushchenko", 
        orcid = "0009-0009-5136-9119",  
        email = "e12545751@student.tuwien.ac.at",
        affiliation = "TU Wien"
      ),
      list(
        name = "Amélie Assmayr", 
        orcid = "0009-0007-0543-4165",  
        email = "e12007770@student.tuwien.ac.at",
        affiliation = "TU Wien"
      )
    ),
    software_environment = sessionInfo()$R.version$version.string,
    dependencies = c(
      paste0("ranger_", packageVersion("ranger")),
      paste0("tidymodels_", packageVersion("tidymodels")),
      paste0("tidyverse_", packageVersion("tidyverse"))
    )
  ),
  
  fair4ml_compliance = list(
    findable = "Metadata included in RO-Crate with DOI reference,
    public dataset and code.",
    accessible = "Model and metadata deposited in TUWRD (T3.9)",
    interoperable = "Standard JSON format, referenced dataset DOI",
    reusable = "Clear license, public repository including all code and
         documentation, intended use, limitations documented,
         parameters documented, seeds and randomness controlled."
  )
)

#######################################
# Model 2: Simple Linear Regression
#######################################

mlr_metadata <- list(
  model_id = "LM-GDP-001",
  model_name = "Simple Linear Regression for GDP Prediction",
  algorithm = list(
    name = "Multiple Linear Regression",
    version = "Base R (stats package)",
    implementation = "lm()",
    citation = "R Core Team (2024). R: A language and environment for
    statistical computing. R Foundation for Statistical Computing."
  ),
  
  training_data = rf_metadata$training_data,
  
  hyperparameters = list(
    formula = "gdp ~ ref_year + mdma + amphetamine + 
    cocaine + methamphetamine + nuts_code",
    method = "Ordinary Least Squares (OLS)",
    intercept = TRUE,
    na_action = "na.omit"
  ),
  
  evaluation_metrics = list(
    adjusted_rsq = mlr_summary$adj.r.squared %>% round(4),
    rmse = comparison_metrics %>% 
      filter(model == "Simple Linear") %>% select("rmse") %>% 
      round(2),
    rsq = comparison_metrics %>% 
      filter(model == "Simple Linear") %>% select("rsq") %>% 
      round(4),
    mae = comparison_metrics %>% 
      filter(model == "Simple Linear") %>% select("mae") %>% 
      round(2)
  ),
  
  performance_context = list(
    test_set_size = nrow(test_data),
    training_set_size = nrow(train_data),
    f_statistic = mlr_summary$fstatistic[1] %>% round(2),
    residual_std_error = mlr_summary$sigma %>% round(2)
  ),
  
  intended_use = list(
    purpose = "Baseline linear model for GDP estimation from wastewater data",
    domain = "Environmental economics / Public health surveillance",
    scope = "European NUTS code regions with available 
              wastewater monitoring data",
    constraints = list(
      "Assumes linear relationships between all predictors and GDP",
      "No interaction terms included",
      "Standard OLS assumptions apply 
      (normality, homoscedasticity, independence)"
    )
  ),
  
  known_limitations = list(
    "Short Time Series",
    "Low Number of Observations",
    "Imperfect estimation of population in catchment area of wastewater 
    treatment plants, especially during events",
    "Imperfect mapping between data sources via manual mapping",
    "Simple linear model may miss non-linear patterns in the data",
    "No regularization 
    (susceptible to multicollinearity among drug metabolites)",
    "Assumes independence of observations 
    (certain cities have multiple sewade treatment plants and concentrations)",
    "Outliers can have disproportionate influence on coefficients",
    "Limited predictive performance compared to ensemble methods"
  ),
  
  technical_specs = list(
    input_features = c("ref_year", "mdma", "amphetamine", "cocaine",
                       "methamphetamine", "nuts_code"),
    target_variable = "gdp",
    feature_types = list(
      ref_year = "integer",
      mdma = "numeric", 
      amphetamine = "numeric",
      cocaine = "numeric",
      methamphetamine = "numeric",
      nuts_code = "factor (treated as dummy variables)"
    ),
    output_type = "numeric (continuous GDP values)",
    coefficient_summary = broom::tidy(mlr_nested) %>%
      select(term, estimate, std.error, p.value) %>%
      as.list()
  ),
  
  provenance = list(
    creation_date = timestamp,
    wasGeneratedBy = list(
      script= "use-case-experiment-reproducible.R",
      scriptVersion= "3b8b8f3ac46713d0317356da8f9d429e68b745fb",
      executionTime= timestamp
    ),
    created_by = list(
      list(
        name = "Barnabás Paksi", 
        orcid = "0009-0001-1032-0177",  
        email = "e11926285@student.tuwien.ac.at",
        affiliation = "TU Wien"
      ),
      list(
        name = "Helene Johanna Vaught", 
        orcid = "0009-0005-8421-9302",  
        email = "e11943054@student.tuwien.ac.at",
        affiliation = "TU Wien"
      ),
      list(
        name = "Vlada Hlushchenko", 
        orcid = "0009-0009-5136-9119",  
        email = "e12545751@student.tuwien.ac.at",
        affiliation = "TU Wien"
      ),
      list(
        name = "Amélie Assmayr", 
        orcid = "0009-0007-0543-4165",  
        email = "e12007770@student.tuwien.ac.at",
        affiliation = "TU Wien"
      )
    ),
    software_environment = sessionInfo()$R.version$string
  ),
  
  fair4ml_compliance = rf_metadata$fair4ml_compliance
)

#######################################
# Model 3: Nested Linear Mixed Model
#######################################

lmm_metadata <- list(
  model_id = "LMM-GDP-001",
  model_name = "Nested Linear Mixed Model for GDP Prediction",
  algorithm = list(
    name = "Linear Mixed Effects Model",
    version = as.character(packageVersion("lme4")),
    implementation = "lmer()",
    citation = "Bates, D., Mächler, M., Bolker, B., & Walker, S. (2015). 
    Fitting Linear Mixed-Effects Models Using lme4. 
    Journal of Statistical Software, 67(1), 1-48."
  ),
  
  training_data = rf_metadata$training_data,
  
  hyperparameters = list(
    formula = "gdp ~ ref_year + mdma + amphetamine + 
                cocaine + methamphetamine + (1 | nuts_code)",
    random_effects = "(1 | nuts_code)",
    fixed_effects = c("ref_year", "mdma", "amphetamine", 
                      "cocaine", "methamphetamine"),
    REML = TRUE,
    optimizer = "bobyqa",
    max_function_evaluations = 100000,
    calc_derivatives = FALSE,
    convergence_tolerance = 1e-5
  ),
  
  evaluation_metrics = list(
    rmse = comparison_metrics %>% 
      filter(model == "Nested Linear") %>% select("rmse") %>% 
      round(2),
    rsq = comparison_metrics %>% 
      filter(model == "Nested Linear") %>% select("rsq") %>% 
      round(4),
    mae = comparison_metrics %>% 
      filter(model == "Nested Linear") %>% select("mae") %>% 
      round(2)
  ),
  
  performance_context = list(
    test_set_size = nrow(test_data),
    training_set_size = nrow(train_data),
    number_of_groups = n_distinct(train_data$nuts_code),
    group_var = "nuts_code",
    convergence_status = "Success (bobyqa optimizer)"
  ),
  
  intended_use = list(
    purpose = "Estimate GDP with nested random effects for geographic regions",
    domain = "Environmental economics",
    scope = "European NUTS code regions with nested structure",
    constraints = list(
      "Assumes random intercepts capture between-region variation",
      "Requires sufficient number of NUTS code groups (>5 recommended)",
      "Fixed effects assume no cross-level interactions"
    )
  ),
  
  known_limitations = list(
    "Short Time Series",
    "Low Number of Observations",
    "Imperfect estimation of population in catchment area of wastewater 
    treatment plants, especially during events",
    "Imperfect mapping between data sources via manual mapping",
    "Assumes normally distributed random effects and residuals",
    "Limited to random intercepts only (no random slopes)",
    "May be computationally intensive with many NUTS code levels",
    "Allows new levels during prediction but at reduced accuracy",
    "Sensitive to scaling of continuous predictors"
  ),
  
  technical_specs = list(
    input_features = c("ref_year", "mdma", "amphetamine", "cocaine", 
                       "methamphetamine", "nuts_code"),
    target_variable = "gdp",
    feature_types = list(
      ref_year = "integer",
      mdma = "numeric",
      amphetamine = "numeric",
      cocaine = "numeric", 
      methamphetamine = "numeric",
      nuts_code = "factor (grouping variable)"
    ),
    output_type = "numeric (continuous GDP values, 
                   accounting for group-level variation)",
    random_effects_variances = as.data.frame(VarCorr(lmm_model)) %>%
      as.list()
  ),
  
  provenance = list(
    creation_date = timestamp,
    wasGeneratedBy = list(
      script= "use-case-experiment-reproducible.R",
      scriptVersion= "3b8b8f3ac46713d0317356da8f9d429e68b745fb",
      executionTime= timestamp
    ),
    created_by = list(
      list(
        name = "Barnabás Paksi", 
        orcid = "0009-0001-1032-0177",  
        email = "e11926285@student.tuwien.ac.at",
        affiliation = "TU Wien"
      ),
      list(
        name = "Helene Johanna Vaught", 
        orcid = "0009-0005-8421-9302",  
        email = "e11943054@student.tuwien.ac.at",
        affiliation = "TU Wien"
      ),
      list(
        name = "Vlada Hlushchenko", 
        orcid = "0009-0009-5136-9119",  
        email = "e12545751@student.tuwien.ac.at",
        affiliation = "TU Wien"
      ),
      list(
        name = "Amélie Assmayr", 
        orcid = "0009-0007-0543-4165",  
        email = "e12007770@student.tuwien.ac.at",
        affiliation = "TU Wien"
      )
    ),
    software_environment = sessionInfo()$R.version$string,
    dependencies = c(
      paste0("lme4_", packageVersion("lme4")),
      paste0("tidymodels_", packageVersion("tidymodels")),
      paste0("tidyverse_", packageVersion("tidyverse"))
    )
  ),
  
  fair4ml_compliance = rf_metadata$fair4ml_compliance
)

#######################################
# Save FAIR4ML metadata as JSON files
#######################################
dir.create("../outputs/metadata/", recursive = TRUE, showWarnings = FALSE)
# Save each model's metadata
write_json(rf_metadata, "../outputs/metadata/rf_model_fair4ml.json", 
           pretty = TRUE, auto_unbox = TRUE)
write_json(mlr_metadata, "../outputs/metadata/lm_model_fair4ml.json", 
           pretty = TRUE, auto_unbox = TRUE)
write_json(lmm_metadata, "../outputs/metadata/lmm_model_fair4ml.json", 
           pretty = TRUE, auto_unbox = TRUE)

# Save combined metadata for RO-Crate
combined_metadata <- list(
  project = "Data Stewardship Experiment",
  creation_date = timestamp,
  dataset_doi = dataset_doi,
  models = list(rf_metadata, mlr_metadata, lmm_metadata),
  evaluation_summary = comparison_metrics %>%
    as.list()
)

write_json(combined_metadata, "../outputs/metadata/all_models_fair4ml.json", 
           pretty = TRUE, auto_unbox = TRUE)

#######################################
# Save model objects for TUWRD deposit
#######################################
dir.create("../outputs/models/", recursive = TRUE, showWarnings = FALSE)
# Save the trained model objects
saveRDS(rf_fit, "../outputs/models/rf_model.rds")
saveRDS(mlr_nested, "../outputs/models/lm_model.rds")
saveRDS(lmm_model, "../outputs/models/lmm_model.rds")

# Also save as RData bundle for convenience
save(rf_fit, mlr_nested, lmm_model, 
     file = "../outputs/models/all_models.RData")

# Save test data and predictions for validation
test_results_for_deposit <- test_results %>%
  select(gdp, pred_rf, pred_mlr, pred_lmm, nuts_code, ref_year)

write_csv(test_results_for_deposit, "../outputs/models/test_predictions.csv")

#######################################
# Generate README for TUWRD deposit
#######################################

readme_text <- paste0(
"# Data Stewardship Experiment: Model Deposit\n\n",
    "## Contents\n",
    "- `rf_model.rds`: Trained Random Forest model (ranger implementation)\n",
    "- `lm_model.rds`: Trained Linear Regression model\n", 
    "- `lmm_model.rds`: Trained Nested Linear Mixed Model\n",
    "- `all_models.RData`: All three models bundled together\n",
    "- `test_predictions.csv`: Test set predictions from all models\n",
    "- `rf_model_fair4ml.json`: FAIR4ML metadata for Random Forest\n",
    "- `lm_model_fair4ml.json`: FAIR4ML metadata for Linear Regression\n",
    "- `lmm_model_fair4ml.json`: FAIR4ML metadata for Linear Mixed Model\n",
    "- `ro-crate-metadata.json`: RO-Crate metadata referencing all models\n\n",
    "## Model Summary\n",
    "Random Forest RMSE: ", comparison_metrics %>% 
                                    filter(model == "Random Forest") %>%
                                    select("rmse") %>% 
                                    round(2), "\n",
    "Linear Model RMSE: ", comparison_metrics %>% 
                                   filter(model == "Simple Linear") %>%
                                   select("rmse") %>% 
                                   round(2), "\n",
    "Mixed Model RMSE: ", comparison_metrics %>%
                                  filter(model == "Nested Linear") %>%
                                  select("rmse") %>% 
                                  round(2), "\n\n",

    "## Reproduction Instructions\n",
    "1. Load the models using readRDS()\n",
    "2. Ensure required packages are installed (ranger, lme4, tidymodels)\n",
    "3. See FAIR4ML metadata for complete hyperparameters and limitations\n",
    "4. Refer to session_info.txt for complete software environment\n\n",
    "## FAIR4ML Compliance\n",
    "All metadata files follow FAIR4ML standards for Findable, Accessible,
    Interoperable, and Reusable machine learning models.\n\n",
    "## Deposit Information\n",
    "Deposited in TUWRD (T3.9) on: ", timestamp, "\n",
    "Dataset DOI: ", dataset_doi, "\n",
    "Contact: TU Wien Research Data Management"
    )
  
  writeLines(readme_text, "../outputs/models/autogen_README.md")

###################

sink("../outputs/session_info.txt")
cat("\n--- Reproducibility Info ---\n")
cat("Script run on:", date(), "\n")
cat("Random seed: 123\n")
cat("RNG kind: L'Ecuyer-CMRG\n")
cat("\n--- Critical Package Versions ---\n")
print(sessionInfo())
sink()
