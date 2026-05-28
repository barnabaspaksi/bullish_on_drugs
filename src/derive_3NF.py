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
    for i in range(2, len(col_names)):
        if col_names[i].startswith('Unnamed:'):
            col_names[i] = f"{col_names[i-1]}_flag"
    gdp_df.columns = col_names
    gdp_df = gdp_df.iloc[1:].reset_index(drop=True)
    gdp_df = gdp_df.loc[:1343,:] # last rows are also metadata which must be manually removed...

    parsed_raw_gdp_df_filepath = os.path.join("../data/processed/", "eurostat_gdp_by_region_2011_2024.csv")
    gdp_df.to_csv(parsed_raw_gdp_df_filepath, encoding = "utf-8")

    return gdp_df

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
    print(set(ww_countries_without_gdp).difference(set(fix_mismatches_cc.keys()).union(unused).union(gdp_unavailable)))        
    
    ww["Country"] = ww["Country"].map(improve_ww_country)

    ww.to_csv(os.path.join("../data/processed/", "euda_wastewater_2011_2025_v2.csv"))
    gdp.to_csv(os.path.join("../data/processed/", "eurostat_gdp_by_region_2011_2024_v2.csv"))

if __name__ == "__main__":

    # ww_df = parse_wastewater_dataset(raw_data_path)    
    # gdp_df = parse_gdp_dataset(raw_data_path)

    align_countries()
    
    

