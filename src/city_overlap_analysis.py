import pandas as pd
import os 
import json 

ww_path = os.path.join("../data/processed/", "euda_wastewater_2011_2025_v2.csv")
gdp_path = os.path.join("../data/processed/", "eurostat_gdp_by_region_2011_2024_v2.csv")
ww = pd.read_csv(ww_path, encoding = "utf-8")
gdp = pd.read_csv(gdp_path, encoding = "utf-8")

num_cities_ww = ww["City"].unique().shape[0] # basis of our analysis

ww_cities = set(ww["City"])
gdp_cities =set(gdp["GEO (Labels)"])

mapping_path = os.path.join("../data/processed/", "city_nuts_mapping_unique.csv")
mapping = pd.read_csv(mapping_path, encoding = "utf-8")
missing_cities = ww_cities.difference(gdp_cities).difference(set(mapping["City"]))

# NOTE: Missing cities ignored. Find explanation in "../data/processed/README.md"
