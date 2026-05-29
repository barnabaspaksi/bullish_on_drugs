import os 
import pandas as pd
from dotenv import load_dotenv
from dbrepo.RestClient import RestClient
from dbrepo.api.dto import TupleUpdate

load_dotenv()
password = os.getenv("DBREPO_PASS")
username = os.getenv("DBREPO_USER")
client = RestClient("https://test.dbrepo.tuwien.ac.at/", username=username, password=password)

DB_ID = os.getenv("DB_ID") #"cf27a11d-58e5-4693-856c-e8f3527e3394" #

def find_tab_id(table_name):
    """We avoid hard-coding values by assuming table names are unique."""
    tables = client.get_tables(database_id=DB_ID)
    for t in tables:
        if t.name == table_name:
            return t.id

def upload_city_map_rows():
    """This wrapper uploads the local data to DBRepo."""
    city_data = pd.read_csv("../data/processed/city_nuts_mapping_3NF.csv", encoding = "utf-8")
    city_data = city_data.drop("City", axis = 1)
    city_data = city_data.loc[:, ["nuts_code", "city_name"]]

    resp = client.import_table_data(
        database_id=DB_ID,
        table_id=find_tab_id(table_name="city_map"),
        dataframe=city_data  
    )

    return resp

def get_tab_schema_cols(tab_name):
    """API forces us to select columns ourselves, so query schema for ordered columns."""
    tab_dbrepo = client.get_table(database_id = DB_ID, table_id = find_tab_id(tab_name))
    cols_from_schema = []
    tab_cols_in_schema = dict(tab_dbrepo)["columns"]
    for c in tab_cols_in_schema:
        cols_from_schema.append(c.name)
    
    return cols_from_schema

def upload_gdp_rows():
    """Select and upload the GDP data according to the DBRepo schema."""
    gdp_data = pd.read_csv("../data/processed/eurostat_gdp_by_region_2011_2024_3NF.csv", encoding = "utf-8")
    gdp_cols = get_tab_schema_cols("gdp_data")
    gdp_cols_final = []
    for c in gdp_cols:
        if c == "gdp_per_cap":
            gdp_cols_final.append("gdp")
        else:
            gdp_cols_final.append(c)

    gdp_data = gdp_data.loc[:, gdp_cols_final]

    resp = client.import_table_data(
        database_id=DB_ID,
        table_id=find_tab_id(table_name="gdp_data"),
        dataframe=gdp_data  
    )

    return resp

def upload_wastewater_rows():
    """Select and upload the Metabolite data according to the DBRepo schema."""
    ww_data = pd.read_csv("../data/processed/euda_wastewater_2011_2024_3NF.csv", encoding = "utf-8")
    ww_cols = get_tab_schema_cols("wastewater_data")
    ww_cols_final = []
    for c in ww_cols:
        if c == "daily_mean":
            ww_cols_final.append("daily_mean_concentration")
        else:
            ww_cols_final.append(c)
    ww_data = ww_data.loc[:, ww_cols_final]

    resp = client.import_table_data(
        database_id=DB_ID,
        table_id=find_tab_id(table_name="wastewater_data"),
        dataframe=ww_data  
    )

    return resp

if __name__ == "__main__":    
    
    resp = upload_city_map_rows()
    print(resp)
    gdp_resp = upload_gdp_rows()
    print(gdp_resp)
    ww_resp = upload_wastewater_rows()
    print(ww_resp)