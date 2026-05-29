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
DB_ID = "cf27a11d-58e5-4693-856c-e8f3527e3394"

