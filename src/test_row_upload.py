from dbrepo.RestClient import RestClient
from dbrepo.api.dto import CreateTable, CreateTableColumn, CreateTableConstraints, CreateForeignKey
import pandas as pd
from pandas.core.interchange.dataframe_protocol import DataFrame
from dotenv import load_dotenv
import os 
from dbrepo.api.dto import CreateView
from dbrepo.api.dto import CreateView, Subset, SubsetColumn, Join
from dbrepo.api.dto import JoinType

load_dotenv()
password = os.getenv("DBREPO_PASS")
username = os.getenv("DBREPO_USER")
client = RestClient("https://test.dbrepo.tuwien.ac.at/", username=username, password=password)

containers = client.get_containers()

container_id = '6cfb3b8e-1792-4e46-871a-f3d103527203'
# DB_ID = "cf27a11d-58e5-4693-856c-e8f3527e3394"
# DB_ID = '9fa181a9-de7c-4d44-b367-517a51f31351'
# dbs = client.get_databases()
# print(dbs)

# db = client.get_database(database_id = '9fa181a9-de7c-4d44-b367-517a51f31351')
# print(db)

def create_city_map_table(database_id):
    """This function collects resources required for creating the manually-compiled mapping table for cities."""
    cols = [
        CreateTableColumn(name="nuts_code", type="varchar", size=5, primary_key=True, null_allowed=False,
                        description="5-character NUTS-3 administrative code (e.g., AT221): https://ec.europa.eu/eurostat/web/nuts"),
        CreateTableColumn(name="city_name", type="varchar", size = 100, primary_key=False, null_allowed=False,
                        description="The name of the city from EUDA/SCODA data (e.g., Graz)"),
    ]

    # define constraints
    cons_city = CreateTableConstraints(primary_key=["nuts_code"], uniques=[["city_name"]])

    df_city = CreateTable(
        name="city_map",
        description="This table serves as the bridge/mapping schema. It resolves the city names used by the EUDA to the NUTS-3 codes used by Eurostat.",
        columns=cols,
        constraints=cons_city,
        is_public=True,
        is_schema_public=True
    )

    response = client._wrapper(
        method="post", 
        url=f'/api/v1/database/{database_id}/table', 
        payload=df_city
    )

    print(f"Response Status: {response.status_code}")
    if response.status_code == 201:
        print("Success! Table created.")
    else:
        print(response.text)

if __name__ == "__main__":
    DB_ID = '9fa181a9-de7c-4d44-b367-517a51f31351'

    create_city_map_table(database_id = DB_ID)

