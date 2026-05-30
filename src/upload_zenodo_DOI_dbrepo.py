from dbrepo.RestClient import RestClient
from dbrepo.api.dto import CreateTable, CreateTableColumn, CreateTableConstraints, CreateForeignKey
import pandas as pd
from pandas.core.interchange.dataframe_protocol import DataFrame
from dotenv import load_dotenv
import os 
from dbrepo.api.dto import CreateView
from dbrepo.api.dto import CreateView, Subset, SubsetColumn, Join
from dbrepo.api.dto import JoinType
from dbrepo.api.dto import (
    CreateIdentifier,
    CreateIdentifierTitle,
    CreateIdentifierDescription,
    RelatedIdentifierType,
    RelatedIdentifierRelation,
    CreateIdentifierCreator,
    CreateRelatedIdentifier,
    DescriptionType,
    IdentifierType,
    License,
    Language,
    SaveRelatedIdentifier
)

load_dotenv()
password = os.getenv("DBREPO_PASS")
username = os.getenv("DBREPO_USER")
client = RestClient("https://test.dbrepo.tuwien.ac.at/", username=username, password=password)

containers = client.get_containers()
print(containers)

container_id = '6cfb3b8e-1792-4e46-871a-f3d103527203'
DB_ID = os.getenv("DB_ID")

related_identifiers = [
        CreateRelatedIdentifier(
            value="10.5281/zenodo.20464726",
            type=RelatedIdentifierType.DOI,
            relation=RelatedIdentifierRelation.IS_SUPPLEMENT_TO
        )
    ]

# class CreateIdentifier(BaseModel):
#     database_id: str
#     type: IdentifierType
#     creators: List[CreateIdentifierCreator]
#     publication_year: int
#     publisher: str
#     titles: List[CreateIdentifierTitle]
#     descriptions: Optional[List[CreateIdentifierDescription]] = None
#     funders: Optional[List[CreateIdentifierFunder]] = None
#     doi: Optional[str] = None
#     language: Optional[str] = None
#     licenses: Optional[List[License]] = None
#     query_id: Optional[str] = None
#     table_id: Optional[str] = None
#     view_id: Optional[str] = None
#     related_identifiers: Optional[List[CreateRelatedIdentifier]] = None
#     publication_day: Optional[int] = None
#     publication_month: Optional[int] = None

titles = [
        CreateIdentifierTitle(
            title="Predictive Modeling of Regional GDP based on Wastewater-Based Epidemiology",
            language=Language.EN
        )
    ]

descriptions = [
        CreateIdentifierDescription(
            description=(
                """Abstract: This use case explores the correlation relationship between 
                illicit drug use in major European cities and their regional economic productivity (GDP). 
                Original Publishers: EUDA & SCORE, EUROSTAT.
                EUDA & SCORE: URI: https://www.euda.europa.eu/data/repository/drugs-municipal-wastewater-europe-source-data-2026_en
                EUROSTAT: DOI: https://doi.org/10.2908/NAMA_10R_3GDP, URI: https://ec.europa.eu/eurostat/databrowser/view/nama_10r_3gdp__custom_20659344/default/table"""
            ),
            type=DescriptionType("Abstract"),
            language=Language.EN
        ),
        CreateIdentifierDescription(
            description=(
                """Data Stewardship and Preprocessing Challenge: While the drug dataset identifies locations 
                by specific city strings (e.g., 'Graz', 'Steyr'), Eurostat utilizes standardized NUTS-3 administrative codes 
                (e.g., 'DE212'). This is resolved via a custom mapping schema table ('city_map').
                Only the active filtered subset utilized in this longitudinal frame is republished here."""
            ),
            type="Methods",
            language=Language.EN
        ),
        CreateIdentifierDescription(
            description=(
                """Temporal & Spatial Coverage: 
                Annual wastewater tracking spans years 2011 to 2025 across 115 cities and 25 countries in the European Union, 
                Norway, and Türkiye. GDP tracking spans annually from 2000 to 2024 across EU Member States, Candidate and 
                potential Candidate Countries, Norway, and Switzerland. Our subset only contains common European countries 
                for the years 2011-2024. Data availability varies across years and regions."""
            ),
            type=DescriptionType("TechnicalInfo"),
            language=Language.EN
        ),
        CreateIdentifierDescription(
            description=(
                """Units of Measure: "
                Wastewater metrics indicate concentrations (mg/1000p/day) of illicit drug loads (Cocaine, Methamphetamine, MDMA) 
                measured from 24-hour composite samples collected over a single week between March and May. 
                GDP values indicate economic output expressed in Euros at current market prices by NUTS 3 region."""
            ),
            type=DescriptionType("Other"),
            language=Language.EN
        )
    ]
    
# 3. Explicit Provenance & Lineage Relationships
related_identifiers = [
    # Upstream Eurostat Source Dataset
    CreateRelatedIdentifier(
        id="10.2908/NAMA_10R_3GDP",
        value="10.2908/NAMA_10R_3GDP",
        type=RelatedIdentifierType.DOI,
        relation=RelatedIdentifierRelation.IS_DERIVED_FROM
    ),
    # Upstream EUDA Open Repository Source
    CreateRelatedIdentifier(
        id="https://www.euda.europa.eu/data/repository/drugs-municipal-wastewater-europe-source-data-2026_en",
        value="https://www.euda.europa.eu/data/repository/drugs-municipal-wastewater-europe-source-data-2026_en",
        type=RelatedIdentifierType.URL,
        relation=RelatedIdentifierRelation.IS_DERIVED_FROM
    )
]
cc_by_4_0 = License(
    identifier="CC-BY-4.0",
    uri="https://creativecommons.org/licenses/by/4.0/",
    description=(
        "Creative Commons Attribution 4.0 International: Allows users to copy, "
        "distribute, display, perform, and modify the work, even for commercial purposes, "
        "provided that they give appropriate credit to the original creator."
    )
)
creators=[
            CreateIdentifierCreator(creator_name="Helene Vaught", firstname= "Helene", lastname= "Vaught", affiliation= "TU Wien"),
            CreateIdentifierCreator(creator_name="Vlada Hlushchenko", firstname= "Vlada", lastname= "Hlushchenko", affiliation= "TU Wien"),
            CreateIdentifierCreator(creator_name="Barnabás Paksi", firstname= "Barnabás", lastname= "Paksi", affiliation= "TU Wien"),
            CreateIdentifierCreator(creator_name="Amélie Assmayr", firstname= "Amélie", lastname= "Assmayr", affiliation= "TU Wien")
        ]


def create_payload_for_table(db_id, tab_id):
    identifier_payload = CreateIdentifier(
            database_id=db_id,
            table_id = tab_id,
            publication_year=2026,           
            publisher="EUDA & SCORE, EUROSTAT, TU Wien",
            type = IdentifierType.TABLE,
            language=Language.EN,
            licenses=[cc_by_4_0],          
            titles=titles,
            descriptions=descriptions,
            related_identifiers=related_identifiers,
            funders= [],
            creators=creators
    )

    return identifier_payload

def create_payload_for_database(db_id):
    return create_payload_for_table(db_id, None)

def upload_zenodo_id_for_db():
    response = client._wrapper(
        method="post", 
        url=f'/api/v1/identifier', 
        payload=create_payload_for_database(DB_ID)
    )
    print(response)
    response.raise_for_status()
    return response

upload_zenodo_id_for_db()

ts = client.get_tables(DB_ID)
table_ids = []
for t in ts:
    table_ids.append(t.id)
    payload = create_payload_for_table(DB_ID, t.id)

    response = client._wrapper(
        method="post", 
        url=f'/api/v1/identifier', 
        payload=payload
    )
    print(response)
    response.raise_for_status()
