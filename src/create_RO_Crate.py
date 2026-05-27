import os
from rocrate.rocrate import ROCrate
from rocrate.model.person import Person
from rocrate.model.contextentity import ContextEntity


def generate_use_case_rocrate():
    crate = ROCrate()

    # ---------------------------------------------------------
    # 1. License and Core Roster (Creators)
    # ---------------------------------------------------------
    # explicit declared open license for both upstream sources
    cc_by_40 = crate.add(ContextEntity(crate, "https://creativecommons.org/licenses/by/4.0/", {
        "@type": "CreativeWork",
        "name": "Creative Commons Attribution 4.0 International",
        "description": "CC-BY-4.0"
    }))

    # map standard DataCite creator
    authors = [
        crate.add(Person(crate, "https://orcid.org/0009-0001-1032-0177", {"name": "Barnabás Paksi", "affiliation": "TU Wien"})),
        crate.add(Person(crate, "https://orcid.org/0009-0005-8421-9302", {"name": "Helene Vaught", "affiliation": "TU Wien"})),
        crate.add(Person(crate, "https://orcid.org/0009-0009-5136-9119", {"name": "Vlada Hlushchenko", "affiliation": "TU Wien"})),
        crate.add(Person(crate, "https://orcid.org/0009-0007-0543-4165", {"name": "Amélie Assmayr", "affiliation": "TU Wien"}))
    ]

    # ---------------------------------------------------------
    # 2. Root Dataset Metadata 
    # ---------------------------------------------------------
    crate.root_dataset["name"] = "Predictive Modeling of Regional GDP per Capita based on Wastewater-Based Epidemiology"
    crate.root_dataset["description"] = (
        "Abstract: This use case explores the correlation relationship between illicit drug use in major European "
        "cities and their regional economic productivity (GDP per capita)"
    )
    crate.root_dataset["datePublished"] = "2026"
    crate.root_dataset["creator"] = authors
    crate.root_dataset["license"] = cc_by_40
    crate.root_dataset["url"] = "https://github.com/barnabaspaksi/bullish_on_drugs"

    # ---------------------------------------------------------
    # 3. Upstream External Input Datasets (Provenance Lineage)
    # ---------------------------------------------------------
    eurostat_gdp = crate.add(ContextEntity(crate, "https://doi.org/10.2908/NAMA_10R_3GDP", {
        "@type": "Dataset",
        "name": "Gross domestic product (GDP) at current market prices by NUTS 3 regions",
        "publisher": "Eurostat",
        "identifier": "10.2908/NAMA_10R_3GDP",
        "description": "Economic baseline metrics for European regions at NUTS-3 level."
    }))

    euda_wastewater = crate.add(ContextEntity(crate, "https://www.euda.europa.eu/data/repository/drugs-municipal-wastewater-europe-source-data-2026_en", {
        "@type": "Dataset",
        "name": "Drugs in municipal wastewater in Europe: Source data 2026",
        "publisher": "EUDA & SCORE",
        "description": "Mass loads (mg/1000p/day) of illicit drug target metabolites captured via wastewater tracking."
    }))

    # ---------------------------------------------------------
    # 4. Local Files: Scripts & Data Structures
    # ---------------------------------------------------------
    # Add files and declare their relationship to the execution

    eurostat_gdp_local_file = crate.add_file("main/data/raw/nama_10r_3gdp__custom_20659344_spreadsheet.csv", properties={
        "name": "Gross domestic product (GDP) at current market prices by NUTS 3 regions",
        "description": "A static snapshot of the Eurostat data downloaded for this specific experiment."
    })

    euda_wastewater_local_file = crate.add_file("main/data/raw/ww2026-all-data_en.csv", properties={
        "name": "Drugs in municipal wastewater in Europe: Source data 2026",
        "description": "A static snapshot of the EUDA/SCORE data downloaded for this specific experiment."
    })

    eurostat_gdp_local_file["isBasedOn"] = eurostat_gdp
    euda_wastewater_local_file["isBasedOn"] = euda_wastewater

    # r script for now, we can gladly still change that to a python file!
    r_script = crate.add_file("use_case_experiment.R", properties={
        "name": "Data Stewardship R Analysis Script",
        "encodingFormat": "text/x-r",
        "description": "Performs data loading, NUTS-3 merging, plotting, and executes ML models (Random Forest, MLR, LMM)."
    })

    # Map DBRepo / TUWRD outputs (replace placeholder URLs with actual final DOIs)
    # Representing the output database / clean data asset in TUWRD
    tuwrd_data_doi = "https://doi.org/10.5072/placeholder-tuwrd-dataset" # Placeholder for TUWRD DOI
    output_dataset = crate.add(ContextEntity(crate, tuwrd_data_doi, {
        "@type": "Dataset",
        "name": "Merged Longitudinal Wastewater and GDP NUTS-3 Frame",
        "description": "Republished active filtered subset utilized in this longitudinal frame, stored inside DBRepo Container ID 6cfb3b8e-1792-4e46-871a-f3d103527203.",
        "license": "CC-BY-4.0"
    }))

    # Formally hook derivation attributes
    output_dataset["isDerivedFrom"] = [eurostat_gdp, euda_wastewater]

    # placeholder for trained model datasets on TUWRD
    trained_models_doi = "https://doi.org/10.5072/tuwrd.placeholder.models"
    models_dataset = crate.add(ContextEntity(crate, trained_models_doi, {
        "@type": "Dataset",
        "name": "Trained Predictive GDP Model Binaries (Random Forest & Nested LMM)",
        "description": "Serialized model weights and architecture binaries generated from the wastewater epidemiology training run.",
        "identifier": "10.5072/tuwrd.placeholder.models"
    }))

    # placeholder for outputs on TUWRD
    trained_models_doi = "https://doi.org/10.5072/tuwrd.placeholder.outputs"
    models_dataset = crate.add(ContextEntity(crate, trained_models_doi, {
        "@type": "Dataset",
        "name": "Outputs from Experiment: PLACEHOLDER! Describe which exactly still",
        "description": "Outputs from the wastewater epidemiology experiment.",
        "identifier": "10.5072/tuwrd.placeholder.models"
    }))

#    ---------------------------------------------------------
    # 5. Computational Workflow Context
    # ---------------------------------------------------------
    
    # computational process: define inputs and outputs
    analysis_action = crate.add(ContextEntity(crate, "#ComputationalAnalysis", {
        "@type": "CreateAction",
        "name": "Execution of R modeling scripts calculating Predictive Modeling of Regional GDP per Capita.",
        "instrument": r_script,
        "object": [eurostat_gdp, euda_wastewater],
        "result": [output_dataset, metrics_csv, models_dataset] 
    }))
    

    # Save to disk (Writes ro-crate-metadata.json directly into the root directory)
    print("Writing ro-crate-metadata.json metadata footprint out...")
    crate.write("./")
    print("Success! file compiled.")

if __name__ == "__main__":
    generate_use_case_rocrate()