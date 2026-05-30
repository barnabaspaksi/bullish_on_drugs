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

#################################
#################################
### Load data
setwd(dirname(this.path()))
final_data_long <- read_csv("../data/processed/joined_data.csv")
head(final_data_long)

final_data <- final_data_long %>% pivot_wider(
  names_from = metabolite_name,
  values_from = daily_mean_concentration
) # we leave NA values bc 0 has true meaning of undetectable quantity

#################################
# plots for exploration 

# correlation plot
cor_data <- final_data %>%
  select(where(is.numeric)) %>%
  cor(use = "pairwise.complete.obs")

# plot as heatmap
heatmap <- ggplot(data = melt(cor_data), aes(x=Var1, y=Var2, fill=value)) + 
  geom_tile() +
  scale_fill_gradient2(low = "blue", high = "red", mid = "white", 
                       midpoint = 0, limit = c(-1,1)) +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, vjust = 1, hjust = 1)) +
  labs(title = "Correlation: illicit drugs and regional GDP", 
       fill = "Correlation", x = "", y="")
heatmap
ggsave("../outputs/correlation_heatmap.png")

# histograms
plot_data <- final_data %>%
  select(where(is.numeric), -ref_year, -gdp) %>%
  pivot_longer(cols = everything(), names_to = "variable", values_to = "value")

# Create a multi-panel histogram
hist_grams <- ggplot(plot_data, aes(x = value)) +
  geom_histogram(bins = 30, fill = "darkgrey", color = "black") +
  facet_wrap(~variable, scales = "free") +
  theme_minimal() +
  labs(title = "Distribution of Model Variables",
       x = "(mg/1000p/day)",
       y = "Frequency")
hist_grams
ggsave("../outputs/concentration_distrib_by_drug.png")

print(final_data)
# target variable histogram 
p1 <- ggplot(final_data, aes(x = log(gdp))) + 
  geom_histogram(fill="darkgrey", color="black", bins = 30) + 
  theme_minimal() +
  labs(title="Distribution of GDP Over Regions", x="Log(Euro)")
p1
ggsave("../outputs/overall_gdp_distribution.png")
#######################################
# split into training and test data

set.seed(123)

# prep data: remove cannabis + ketamine
ml_data <- final_data %>%
  select(gdp, ref_year, amphetamine, nuts_code, methamphetamine, cocaine, mdma) %>%
  mutate(nuts_code = as.character(nuts_code)) %>%
  drop_na()

data_split <- sample(nrow(ml_data),round(nrow(ml_data)*0.8))
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
rf_fit <- ranger(gdp ~ ref_year + mdma + amphetamine + cocaine + methamphetamine + nuts_code, data = train_data, importance = 'impurity')

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
combines_plots <- p3 + p4


######################################
# fit model: Nested linear regression

lmm_model <- lmer(gdp ~  ref_year + mdma + amphetamine + cocaine + methamphetamine + (1 | nuts_code), 
                  data = train_data)

######################################
# compare all results 

test_results <- test_data %>%
  mutate(pred_rf = test_data$rf_pred,
         pred_mlr = test_data$mlr_pred,
         pred_lmm = predict(lmm_model, newdata = test_data, allow.new.levels = TRUE),
         pred_rf  = pmax(pred_rf, 0),
         pred_mlr = pmax(pred_mlr, 0),
         pred_lmm = pmax(pred_lmm, 0))

plot_comparison <- test_results %>%
  select(gdp, pred_rf, pred_mlr, pred_lmm) %>%
  pivot_longer(cols = starts_with("pred"), names_to = "model", values_to = "prediction") %>%
  mutate(model = ifelse(model == "pred_rf", "Random Forest", ifelse(model == "pred_mlr", "Simple Linear", "Nested Linear")))

results_plot <- ggplot(plot_comparison, aes(x = gdp/1000000, y = prediction/1000000, color = model)) +
  geom_point(alpha = 1) +
  geom_abline(slope = 1, intercept = 0, linetype = "dashed", color = "darkgrey") +
  facet_wrap(~model) +
  theme_minimal() +
  expand_limits(x = 0, y = 0) +
  labs(title = "Experiment Results: Predicted vs. Actual GDP",
       x = "Actual GDP (Euro/M)",
       y = "Predicted GDP (Euro/M)") +
  scale_color_manual(values = c("Random Forest" = "cornflowerblue", "Simple Linear" = "darkorchid", "Nested Linear" = "hotpink2"))

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
#write_csv(comparison_metrics, "model_metrics_comparison.csv")

