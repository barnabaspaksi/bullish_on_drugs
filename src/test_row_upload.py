import os 
from dotenv import load_dotenv
from dbrepo.RestClient import RestClient
from dbrepo.api.dto import CreateTable, CreateTableColumn, CreateTableConstraints, CreateForeignKey

load_dotenv()
password = os.getenv("DBREPO_PASS")
username = os.getenv("DBREPO_USER")
client = RestClient("https://test.dbrepo.tuwien.ac.at/", username=username, password=password)

def create_city_map_table(database_id):
    """This function collects resources required for creating the manually-compiled mapping table for cities."""
    cols = [
        CreateTableColumn(name="nuts_code", type="varchar", size=5, primary_key=True, null_allowed=False,
                        #concept_uri="http://purl.org/linked-data/sdmx/2009/dimension#refArea",
                        description="5-character NUTS-3 administrative code (e.g., AT221): https://ec.europa.eu/eurostat/web/nuts"),
                        
        CreateTableColumn(name="city_name", type="varchar", size = 100, primary_key=False, null_allowed=False,
                        #concept_uri= "http://purl.obolibrary.org/obo/NCIT_C95378",
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

def create_gdp_table(database_id):
    """This function collects resources required for creating the GDP table."""
    cols_gdp = [
        CreateTableColumn(name="nuts_code", type="varchar", size=5, primary_key=True, null_allowed=False,
                        description="5-character NUTS-3 administrative code (e.g. AT221): https://ec.europa.eu/eurostat/web/nuts"),
        CreateTableColumn(name="ref_year", type="int", primary_key=True, null_allowed=False,
                        #concept_uri= "http://rs.tdwg.org/dwc/terms/year",
                        description="4-digit year of the record: 2011 to 2024"),
        CreateTableColumn(name="gdp", type="int", size = 30, primary_key=False, null_allowed=True,
                        #concept_uri= "http://purl.org/linked-data/sdmx/2009/measure#obsValue",
                        #unit_uri= "https://www.omg.org/spec/Commons/QuantitiesAndUnits/QuantityValue",
                        description="Gross Domestic Product by NUTS Code"),
        CreateTableColumn(name="currency", type="varchar", size = 10, primary_key=False, null_allowed=True,
                        #concept_uri= "http://purl.org/linked-data/sdmx/2009/attribute#currency",
                        #unit_uri= "https://www.omg.org/spec/Commons/QuantitiesAndUnits/hasUnit",
                        description="Currency pertaining to the Gross Domestic Product (in gdp column)")
    ]

    foreign_keys_gdp = [
        CreateForeignKey(
            columns=["nuts_code"],           
            referenced_table="city_map", 
            referenced_columns=["nuts_code"] 
        )
    ]

    cons_gdp = CreateTableConstraints(
        primary_key=["nuts_code", "ref_year"],
        foreign_keys=foreign_keys_gdp
    )

    df_gdp = CreateTable(
        name="gdp_data",
        description="This table stores the economic baseline for European regions (gross domestic product at current market prices by NUTS3 regions). Sourced from Eurostat.",
        columns=cols_gdp,
        constraints=cons_gdp,
        is_public=True,
        is_schema_public=True
    )

    response = client._wrapper(
        method="post", 
        url=f'/api/v1/database/{database_id}/table', 
        payload=df_gdp
    )
    print(response)

def create_wastewater_table(database_id):
    """This function collects resources required for creating the wastewater metabolite concentration table."""
    cols = [
        CreateTableColumn(name="city_name", type="varchar", size = 100, primary_key=True, null_allowed=False,
                        description="The name of the city from EUDA/SCODA data (e.g., Graz)"),
        CreateTableColumn(name="ref_year", type="int", primary_key=True, null_allowed=False,
                        description="4-digit year of the record: 2011 to 2024"),
        CreateTableColumn(name="metabolite_name", type="varchar", size=100, primary_key=True, null_allowed=False,
                        #concept_uri= "http://purl.obolibrary.org/obo/CHEBI_23367",        
                        description="The specific substance whose concentration was estimated (e.g., Cocaine, MDMA)"),
        CreateTableColumn(name="daily_mean_concentration", type="decimal", size=15, d=2, primary_key=False, null_allowed=True,
                        #concept_uri= "http://purl.allotrope.org/ontologies/process#AFP_0002800",
                        #unit_uri= "https://www.omg.org/spec/Commons/QuantitiesAndUnits/DerivedUnit",
                        description="(mg/1000person/day) Daily averages of metabolite concentration scaled by the population estimates. Values below the method limit of quantification are indicated as zero.")
    ]

    foreign_keys_waste = [
        CreateForeignKey(
            columns=["city_name"],           
            referenced_table="city_map", 
            referenced_columns=["city_name"] # Points to the Unique column
        )
    ]

    cons_waste = CreateTableConstraints(
        primary_key=["city_name", "ref_year", "metabolite_name"],
        foreign_keys=foreign_keys_waste
    )

    df_wastewater_data = CreateTable(
        name="wastewater_data",
        description="Estimated concentrations of metabolites in municipal wastewater for various cities over the period of 2011-2024. Sourced from EUDA and SCORE",
        columns=cols,
        constraints=cons_waste,
        is_public=True,
        is_schema_public=True
    )

    # call wrapper with the object
    response = client._wrapper(
        method="post", 
        url=f'/api/v1/database/{database_id}/table', 
        payload=df_wastewater_data
    )

    print(f"Response Status: {response.status_code}")
    if response.status_code == 201:
        print("Success! Table created.")
    else:
        print(response.text)

if __name__ == "__main__":
    DB_ID = os.getenv("DB_ID") 

    create_city_map_table(database_id = DB_ID)
    create_gdp_table(database_id = DB_ID)
    create_wastewater_table(database_id = DB_ID)

    # db = client.get_tables(database_id = DB_ID)
    # print(db)
