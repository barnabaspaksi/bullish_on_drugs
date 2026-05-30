import pandas as pd

ww = pd.read_csv("../data/processed/euda_wastewater_2011_2024_3NF.csv").drop("Unnamed: 0", axis = 1)
ww["metabolite_name"] = ww["metabolite_name"].str.lower()
ww_ref = pd.read_csv("../data/processed/wastewater_3NF_reference.csv")
ww_ref["metabolite_name"] = ww_ref["metabolite_name"].str.lower()
orig_cities = set(ww_ref["city"])
cities_3nf = set(ww["city_name"])

assert orig_cities.difference(cities_3nf) == cities_3nf.difference(orig_cities) == set()
assert ww_ref.shape == ww.shape

rename_cols = {'city' : "city_name",
               'year' : "ref_year",
               'metabolite_name' : "metabolite_name",
               'daily_mean_concentration' : "daily_mean_concentration"}
ww_ref = ww_ref.rename(columns=rename_cols)
ww_ref_prepped = ww_ref.sort_values(["city_name", "ref_year", "metabolite_name"]).reset_index(drop=True)
ww_prepped = ww.sort_values(["city_name", "ref_year", "metabolite_name"]).reset_index(drop=True)

assert ww_prepped.compare(ww_ref_prepped, keep_equal=True).empty
