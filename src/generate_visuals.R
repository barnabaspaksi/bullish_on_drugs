#################################
## Pre-ML Exploratory Analysis ##
#################################

### Packages
library(this.path)
library(readr)
library(tidyverse)
library(knitr)

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

# target variable histogram 
p1 <- ggplot(final_data, aes(x = log(gdp))) + 
  geom_histogram(fill="darkgrey", color="black", bins = 30) + 
  theme_minimal() +
  labs(title="Distribution of GDP Over Regions", x="Log(Euro)")
p1
ggsave("../outputs/overall_gdp_distribution.png")