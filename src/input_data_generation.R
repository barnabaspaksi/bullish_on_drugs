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
ww2026_all_data_en <- read_csv("../Data/Input/ww2026-all-data_en.csv", locale = locale(encoding = "latin1"))
head(ww2026_all_data_en, 10)

gdp_NUTS3 <- read_excel("../Data/Input/nama_10r_3gdp__custom_20659344_spreadsheet_CODES.xlsx", skip = 7)
head(gdp_NUTS3)

#################################
#################################
## Look at and clean data

# cleaning gdp data
gdp_long <- gdp_NUTS3 %>%
  # get rid of empty first row
  slice(-1) %>%
  #select(where(~ !all(is.na(.)))) %>%
  rename(nuts_code = 1, region_label = 2) %>% # rename first two variables
  # select only NUTS code and the 4-digit year columns
  select(nuts_code, matches("^[0-9]{4}$")) %>% 
  # make year columns to character so they can be combined
  mutate(across(matches("^[0-9]{4}$"), as.character)) %>% 
  
  # format to long
  pivot_longer(
    cols = -nuts_code, 
    names_to = "year", 
    values_to = "gdp_per_cap"
  ) %>%
  mutate(
    year = as.numeric(year),
    gdp_per_cap = as.numeric(gdp_per_cap),
    nuts_code = str_trim(nuts_code)
  ) %>%
  # make sure NUTS3 are used
  filter(nchar(nuts_code) == 5) %>%
  drop_na(gdp_per_cap) %>%
  mutate(gdp_millions = gdp_per_cap / 1000000
         ) %>%
  mutate(gdp = gdp_per_cap * 1000000)

#gdp_long$gdp_per_cap <- gdp_long$gdp_per_cap/1000

# check data
head(gdp_long)

#################################
# cleaning waterwaste drug data
unique(ww2026_all_data_en$City) # --> manually look for NUT3 codes

# Load the NUTS map from the external CSV file
city_map <- read_csv("../Data/Output/city_nuts_mapping_unique.csv")

# use map to select cities that have NUT code
ww_with_nuts <- ww2026_all_data_en %>% 
  inner_join(city_map, by = "City")

# clean + wide format
ww_wide <- ww_with_nuts %>%
  select(City, Year, Metabolite, `Daily mean`) %>%
  mutate(Year = as.numeric(Year)) %>%
  group_by(City, Year, Metabolite) %>%
  summarise(`Daily mean` = mean(`Daily mean`, na.rm = TRUE), .groups = "drop") %>%
  pivot_wider(names_from = Metabolite, values_from = `Daily mean`)

# make colnames lowercase for easier merging
ww_wide <- ww_wide %>%
  rename_with(tolower)

city_map <- city_map %>%
  rename_with(tolower)

#################################
### REPRODUCE DATASETS IN 3NF
print(dim(gdp_long))
print(min(gdp_long["year"]))

gdp_semi <- inner_join(city_map, gdp_long, by = "nuts_code")
print(dim(gdp_semi)) # SEEMS CORRECT

print(dim(ww_wide))
print(ww_wide)
ww_wide <- ww_wide %>% filter(year != 2025)
  
ww_long <- pivot_longer(
  ww_wide,
  cols = c(mdma, amphetamine, cannabis, cocaine, methamphetamine, ketamine),
  names_to = "metabolite_name",
  values_to = "daily_mean_concentration"  
  ) %>% select(
  "city", "year", "metabolite_name", "daily_mean_concentration"
  ) %>% drop_na(
    daily_mean_concentration
    ) %>% filter(!city %in% c("London", "Bristol", "Sarajevo"))


print(dim(ww_long))
print(head(ww_long))
write_csv(ww_long, "wastewater_3NF_reference.csv")

ww_long_with_nuts <- ww_long %>% 
  inner_join(city_map, by = "city")

################################
# join waste drug data with gdp 

data_merge <- inner_join(ww_long_with_nuts, gdp_long, by = c("nuts_code", "year"))
final_data <- data_merge %>%
  select(where(~ !all(is.na(.))), -c(gdp_millions, gdp_per_cap))
print(dim(final_data))
print(head(final_data))
write_csv(final_data, "joined_data_expected.csv")
