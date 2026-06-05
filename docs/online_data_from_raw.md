## How to create data for DBRepo (3NF from raw data)

<br> **Step 1**: derive_3NF creates the local files from the raw ones in the format which fits the schema. In particular, only rows which have a join partner may be uploaded. 
<br> **Step 2**: create_db_dbrepo.py is run to create a new db. The id must be added to dotenv: DB_ID=5cde660e-153a-4bff-8e41-69e87cda399d 
<br> **Step 3**: create_tables_dbrepo.ipynb is executed to initalize table schemas and basic type stuff (part of T2.1) 
<br> **Step 4**: upload_metadata_dbrepo.ipynb adds licensing info and some metadata (end of T2.1) 
<br> **Step 5**: semantic_mapping.ipynb can be run completely to add the concept_uri and unit_uri stuff to tables which are dedicated fields by default, not something we need to create as identifiers. (T2.2 and T2.3 are done together and complete)
<br> **Step 6**: create_views_dbrepo.ipynb is Amy's part but renamed and also running on the DB_ID from dotenv. It has the mistake of aggregations in objects which do not have that parameter, so these views are incorrect afaik (T2.4). Although I added currency as a column to gdp, it is not needed for analysis, so I left the views and only changed column names where necessary, for example daily_mean is not daily_mean_concentration.
<br> **Step 7**: upload_data_to_dbrepo.py is my solution for populating the tables with data. It works only when GDP is not an int, as those only allow numbers until 2 billion and some regions have higher GDPs. This is why I reran the entire pipeline documented here. (This concludes T2.5)
