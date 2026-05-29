import os 
import pandas as pd
import json 

raw_data_path = "../data/raw/"
raw_files = os.listdir(raw_data_path)

orig_filenames = ['nama_10r_3gdp__custom_20659344_spreadsheet.csv', 'ww2026-all-data_en.csv']

fix_mismatches_cc = {
                "H" : "HU",
                "GR" : "EL",
                'GB' : "UK"
            }

def parse_gdp_dataset(raw_data_path):
    """
    Get the data from the original file without metadata. 
    Write the output to a more conveniently usable CSV.
    """
    num_metadata_lines_at_start = 7
    gdp_file = os.path.join(raw_data_path, 'nama_10r_3gdp__custom_20659344_spreadsheet.csv')
    gdp_df = pd.read_csv(gdp_file, encoding='utf-8', skiprows=num_metadata_lines_at_start, thousands=',')
    col_names = list(gdp_df.columns)
    col_names[0] = gdp_df.iloc[0, 0]  # Becomes 'GEO (Codes)'
    col_names[1] = gdp_df.iloc[0, 1]  # Becomes 'GEO (Labels)'

    # Rename the 'Unnamed' flag columns dynamically to '<Year>_flag' 
    # (e.g., p for provisional, e for estimated, b for break in time series)
    remove_flag_cols = []
    for i in range(2, len(col_names)):
        if col_names[i].startswith('Unnamed:'):
            col_names[i] = f"{col_names[i-1]}_flag"
            remove_flag_cols.append(col_names[i])
    gdp_df.columns = col_names
    gdp_df = gdp_df.drop(remove_flag_cols, axis = 1)
    gdp_df = gdp_df.iloc[1:].reset_index(drop=True)
    gdp_df = gdp_df.loc[:1343,:] # last rows are also metadata which must be manually removed...
    df_long = gdp_df.melt(
        id_vars=["GEO (Codes)", "GEO (Labels)"],  
        var_name="Year",                                      
        value_name="GDP (M EUR)"                                       
    )

    # We exclude totals for EU, as we are interested in local analysis
    df_badnuts = df_long[df_long["GEO (Codes)"].map(lambda x: len(x) > 5)].index    
    df_long = df_long.drop(df_badnuts) 

    parsed_raw_gdp_df_filepath = os.path.join("../data/processed/", "eurostat_gdp_by_region_2011_2024.csv")
    df_long.to_csv(parsed_raw_gdp_df_filepath, encoding = "utf-8")
    
    return df_long

def parse_wastewater_dataset(raw_data_path):
    """
    Get the data from the original file and change encoding to utf-8.
    Write the output to a more conveniently usable CSV.
    """
    wwater_file = os.path.join(raw_data_path, 'ww2026-all-data_en.csv')
    ww = pd.read_csv(wwater_file, encoding ="latin1")
    parsed_raw_ww_filepath = os.path.join("../data/processed/", "euda_wastewater_2011_2025.csv")
    ww.to_csv(parsed_raw_ww_filepath, encoding = "utf-8")

    return ww

def improve_ww_country(country_code):        
    """Reassign country codes based on usage in the """
    if country_code in fix_mismatches_cc:
        return fix_mismatches_cc[country_code]
    else:
        return country_code

def align_countries():
    """
    Ensure that countries which appear in both data sources are not missed.
    Write the results to new CSV files with a new Country field.
    """
    ww_path = os.path.join("../data/processed/", "euda_wastewater_2011_2025.csv")
    gdp_path = os.path.join("../data/processed/", "eurostat_gdp_by_region_2011_2024.csv")
        
    ww = pd.read_csv(ww_path, encoding = "utf-8")
    gdp = pd.read_csv(gdp_path, encoding = "utf-8")

    gdp_countries = gdp['GEO (Codes)'].map(lambda x: str(x)[:2])
    gdp["Country"] = gdp_countries
    ww_countries = ww["Country"].unique()    
    ww_countries_without_gdp = list(set(ww_countries).difference(set(gdp_countries)))        
    
    unused = {"CL", 'US', "KR", "CA", "NZ", 'AU', 'BR'}
    gdp_unavailable = {"IS", "BA", "UK", "GB"} # Europe but not EU -> no GDP data 
    assert len(set(ww_countries_without_gdp).difference(set(fix_mismatches_cc.keys()).union(unused).union(gdp_unavailable))) == 0        
    
    ww["Country"] = ww["Country"].map(improve_ww_country)
    ww_eu = ww[ww["Country"].map(lambda x: x not in unused.union(gdp_unavailable)) == True]

    ww_eu.to_csv(os.path.join("../data/processed/", "euda_wastewater_2011_2025_v2.csv"))
    gdp.to_csv(os.path.join("../data/processed/", "eurostat_gdp_by_region_2011_2024_v2.csv"))

def write_finals(ww, gdp, mapping):
    """Persist the dataframes with the planned schema
    before the join so they can be uploaded to DBRepo."""
    assert type(ww) == type(gdp) == type(mapping) == pd.DataFrame

    mapping = mapping.rename(columns={"City":"city_name"})

    gdp["gdp"] = gdp["GDP (M EUR)"].map(lambda x: 1000000 * x)
    gdp["currency"] = "EUR"
    gdp = gdp.rename(columns = {'GEO (Codes)' : "nuts_code",
                                "Year" : "ref_year"
                                })
    gdp = gdp.loc[:, ["nuts_code", "ref_year", "gdp", "currency"]]

    ww = ww.rename(columns = {"Metabolite" : "metabolite_name",
                                "Year" : "ref_year",
                                "Daily mean" : "daily_mean_concentration",
                                "City" : "city_name"
                                })
    ww = ww.loc[:, ["city_name", "ref_year", "metabolite_name", "daily_mean_concentration"]]
    
    mapping.to_csv(os.path.join("../data/processed/", "city_nuts_mapping_3NF.csv"), encoding = "utf-8")
    ww.to_csv(os.path.join("../data/processed/", "euda_wastewater_2011_2024_3NF.csv"), encoding = "utf-8")
    gdp.to_csv(os.path.join("../data/processed/", "eurostat_gdp_by_region_2011_2024_3NF.csv"), encoding = "utf-8")

def join_datasets():
    ww_path = os.path.join("../data/processed/", "euda_wastewater_2011_2025_v2.csv")
    gdp_path = os.path.join("../data/processed/", "eurostat_gdp_by_region_2011_2024_v2.csv")
    mapping_path = os.path.join("../data/processed/", "city_nuts_mapping_unique.csv")

    ww = pd.read_csv(ww_path, encoding = "utf-8")
    gdp = pd.read_csv(gdp_path, encoding = "utf-8")
    mapping = pd.read_csv(mapping_path, encoding = "utf-8")
    mapping.index = mapping["City"].str.lower()
    mapping_df = mapping
    mapping = mapping["nuts_code"].to_dict()

    ww["nuts_code"] = ww["City"].str.lower().map(mapping)
    ww = ww[~ww["nuts_code"].isna()]
    ww["Year"] = ww["Year"].astype(int)
    ww["nuts_code"] = ww["nuts_code"].astype(str).map(str.strip)
    ww = ww[ww["Year"] != 2025]

    gdp["Year"] = gdp["Year"].astype(int)
    gdp["GEO (Codes)"] = gdp["GEO (Codes)"].astype(str).map(str.strip)
    gdp = gdp[gdp["GDP (M EUR)"] != ":"]

    ww = ww.drop(["Unnamed: 0.1", "Unnamed: 0"], axis = 1)
    gdp = gdp.drop(["Unnamed: 0.1", "Unnamed: 0"], axis = 1)
    gdp["GDP (M EUR)"] = gdp["GDP (M EUR)"].str.replace(",", "").astype(float)   

    write_finals(ww, gdp, mapping_df)

    # Creating reference data to compare with the joined view we create from DBRepo tables
    ww_with_gdp = ww.merge(gdp, how = "inner", left_on = ["nuts_code", "Year"], right_on = ["GEO (Codes)", "Year"])
    
    country_match = ww_with_gdp.apply(lambda x: x.loc["Country_x"] == x.loc["Country_y"], axis =1).value_counts()
    assert country_match.get(True, 0) == ww_with_gdp.shape[0] # this ensures that uploading the country to DBRepo is not needed
    
    joined_df_path = os.path.join("../data/processed/", "wastewater_with_gdp_2011_2024.csv")
    ww_with_gdp.to_csv(joined_df_path, encoding = "utf-8")

    return ww_with_gdp
    

if __name__ == "__main__":

    ww_df = parse_wastewater_dataset(raw_data_path)    
    gdp_df = parse_gdp_dataset(raw_data_path)

    align_countries()
    join_datasets()   
