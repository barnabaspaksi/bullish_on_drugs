import os 
import json 
from dotenv import load_dotenv
from dbrepo.RestClient import RestClient
from dbrepo.api.dto import CreateDatabase

load_dotenv()
password = os.getenv("DBREPO_PASS")
username = os.getenv("DBREPO_USER")
client = RestClient("https://test.dbrepo.tuwien.ac.at/", username=username, password=password)

containers = client.get_containers()

def create_database(client, db_config):
    """We redefine this method due to the misalignment between the API and the actual package interfaces."""
    url = f'/api/v1/database'
    response = client._wrapper(method="post", url=url, force_auth=True,
                                payload=db_config)
    
    return response

def create_db_from_params(client, container_id, db_name, is_public = True, is_schema_public = True):
    """We allow users to pass the relevant parameters only 
    to avoid dealing with the pointless wrappers from the package which break a lot anyway."""
    new_db_config = CreateDatabase(
        name = db_name,
        container_id = container_id,
        is_public=True,
        is_schema_public=True,
        
    )

    resp = create_database(client, db_config=new_db_config)
    resp.raise_for_status()

    if resp.status_code == 201:
        resp_obj = json.loads(resp.text)
        our_db = resp_obj["id"]
    
        return our_db
    
    else:
        return resp.text

if __name__ == "__main__":
    container_id = "6cfb3b8e-1792-4e46-871a-f3d103527203"
    db_creation_resp = create_db_from_params(client=client,
                                            container_id=container_id,
                                            db_name="dast_g20_wastewater_epidemiology")