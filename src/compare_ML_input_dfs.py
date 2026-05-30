import pandas as pd

ww = pd.read_csv("../data/processed/euda_wastewater_2011_2024_3NF.csv").drop("Unnamed: 0", axis = 1)
ww["metabolite_name"] = ww["metabolite_name"].str.lower()
ww_ref = pd.read_csv("C:/Users/Bhar2/Downloads/Part1/Part1/Code/wastewater_3NF_reference.csv")
ww_ref["metabolite_name"] = ww_ref["metabolite_name"].str.lower()
orig_cities = set(ww_ref["city"])
cities_3nf = set(ww["city_name"])

print(orig_cities.difference(cities_3nf))
print(cities_3nf.difference(orig_cities))
ww_ref_eu = ww_ref[(ww_ref["city"] != 'Sarajevo')&(ww_ref["city"] != 'Bristol')&(ww_ref["city"] != 'London')]

res = ww.merge(ww_ref_eu, how = "left", left_on =["city_name", "ref_year", "metabolite_name"], right_on = ["city", "year", "metabolite_name"] )
matching = res.apply(lambda x: x.loc["daily_mean_concentration_x"] == x.loc["daily_mean_concentration_y"], axis = 1)

print(res.loc[matching[matching == False].index, :])
