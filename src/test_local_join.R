#################################
## Data Stewardship Experiment ##
#################################

### Packages
library(this.path) # needed to avoid absolute paths (weird in R)
library(readr)
library(dplyr)
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
ww <- read_csv("../data/processed/euda_wastewater_2011_2024_3NF.csv")
ww <- ww %>% select("city_name", "ref_year", 
              "metabolite_name", "daily_mean_concentration")

gdp <- read_csv("../data/processed/eurostat_gdp_by_region_2011_2024_3NF.csv")
gdp <- gdp %>% select("nuts_code", "ref_year", "gdp")
mapping <- read_csv("../data/processed/city_nuts_mapping_3NF.csv")
mapping <- mapping %>% select("city_name", "nuts_code")
head(ww)
head(gdp)
head(mapping)

ww2 <- inner_join(ww, mapping, by = "city_name")
joined_data <- inner_join(gdp, ww2, by = c("nuts_code", "ref_year"))
head(joined_data)

write.csv(joined_data, "../data/processed/joined_data.csv", row.names = FALSE)
