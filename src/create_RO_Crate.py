import os
import json
from rocrate.rocrate import ROCrate
from rocrate.model.person import Person
from rocrate.model.contextentity import ContextEntity


def generate_use_case_rocrate():
    crate = ROCrate()

    # ---------------------------------------------------------
    # License and Core Roster (Creators)
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
    # Root Dataset Metadata 
    # ---------------------------------------------------------
    crate.root_dataset["name"] = "Predictive Modeling of Regional GDP based on Wastewater-Based Epidemiology"
    crate.root_dataset["description"] = (
        "Abstract: This use case explores the correlation relationship between illicit drug use in major European "
        "cities and their regional economic productivity (GDP per NUTS3 region)"
    )
    crate.root_dataset["datePublished"] = "2026"
    crate.root_dataset["creator"] = authors
    crate.root_dataset["license"] = cc_by_40
    crate.root_dataset["url"] = "https://github.com/barnabaspaksi/bullish_on_drugs"

    # ---------------------------------------------------------
    # Upstream External Input Datasets (Provenance Lineage)
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
    # Local Files: Scripts & Data Structures
    # ---------------------------------------------------------
    # Add files and declare their relationship to the execution

    eurostat_gdp_local_file = crate.add_file("./data/raw/nama_10r_3gdp__custom_20659344_spreadsheet.csv",
                                             dest_path="./data/raw/nama_10r_3gdp__custom_20659344_spreadsheet.csv", properties={
        "name": "Gross domestic product (GDP) at current market prices by NUTS 3 regions",
        "description": "A static snapshot of the Eurostat data downloaded for this specific experiment."
    })

    euda_wastewater_local_file = crate.add_file("./data/raw/ww2026-all-data_en.csv", 
                                                dest_path="./data/raw/ww2026-all-data_en.csv", properties={
        "name": "Drugs in municipal wastewater in Europe: Source data 2026",
        "description": "A static snapshot of the EUDA/SCORE data downloaded for this specific experiment."
    })

    eurostat_gdp_local_file["isBasedOn"] = eurostat_gdp
    euda_wastewater_local_file["isBasedOn"] = euda_wastewater

    # r script for now, we can gladly still change that to a python file!
    r_script = crate.add_file("src/use-case-experiment-reproducible.R", 
                              dest_path="src/use-case-experiment-reproducible.R", properties={
        "name": "Data Stewardship Experiment",
        "encodingFormat": "text/x-r",
        "description": "Runs the experiment: performs data loading, NUTS-3 merging, plotting, and executes ML models (Random Forest, MLR, LMM)."
    })

    # Map DBRepo 
    tuwrd_data_doi = "https://doi.org/0.82556/pbwe-bk06" 
    output_dataset = crate.add(ContextEntity(crate, tuwrd_data_doi, {
        "@type": "Dataset",
        "name": "Merged Longitudinal Wastewater and GDP NUTS-3 Frame",
        "description": "Republished active filtered subset utilized in this longitudinal frame, stored inside DBRepo Container ID 6cfb3b8e-1792-4e46-871a-f3d103527203.",
        "license": "CC-BY-4.0"
    }))

    # Formally hook derivation attributes
    output_dataset["isBasedOn"] = [eurostat_gdp, euda_wastewater]

    # placeholder for trained model datasets on TUWRD
    trained_models_doi = "https://doi.org/10.70124/acbj8-58e25"
    models_TUWRD = crate.add(ContextEntity(crate, trained_models_doi, {
        "@type": "Dataset",
        "name": "Models: Predictive Modeling of Regional GDP based on Wastewater-Based Epidemiology.",
        "description": "Trained machine learning models (Random Forest Regression, Multiple Linear Regression, and a Nested Linear Mixed Model) to explore the relationship between illicit drug consumption and regional economic productivity (GDP) across European cities. The models attempt to predict economic output using wastewater metabolite concentrations (MDMA, amphetamine, cocaine, methamphetamine), temporal data, and NUTS-3 regional administrative codes.",
        "identifier": "10.5072/tuwrd.placeholder.models"
    }))

    # placeholder for outputs on TUWRD
    outputs_doi = "https://doi.org/10.70124/x3jty-5c735"
    outputs_TUWRD = crate.add(ContextEntity(crate, outputs_doi, {
        "@type": "Dataset",
        "name": "Generated Outputs: Predictive Modeling of Regional GDP based on Wastewater-Based Epidemiology.",
        "description": "Outputs of experiment investigating the relationship between illicit drug metabolite concentrations in municipal wastewater and regional GDP across European cities. The purpose of this dataset is to document the evaluation results and visualizations produced by three regression models (Random Forest Regression, Multiple Linear Regression, and a Nested Linear Mixed Model). ",
        "identifier": "10.5072/tuwrd.placeholder.models"
    }))

    # ---------------------------------------------------------
    # Adding the Model Card (Task T3.5)
    # ---------------------------------------------------------

    lm_model_card = crate.add_file("./outputs/metadata/modelcard_lm.md",
                                   dest_path="./outputs/metadata/modelcard_lm.md", properties={
        "name": "Model Card for Trained Linear Regression model",
        "encodingFormat": "text/markdown",
        "description": "Model card describing intended use, training data, evaluation metrics, and limitations."
    })

    lmm_model_card = crate.add_file("./outputs/metadata/modelcard_lmm.md",
                                   dest_path="./outputs/metadata/modelcard_lmm.md", properties={
        "name": "Model Card for Trained Nested Linear Mixed Model",
        "encodingFormat": "text/markdown",
        "description": "Model card describing intended use, training data, evaluation metrics, and limitations."
    })

    rf_model_card = crate.add_file("./outputs/metadata/modelcard_rf.md",
                                    dest_path="./outputs/metadata/modelcard_rf.md", properties={
        "name": "Model Card for Trained Random Forest model (ranger implementation)",
        "encodingFormat": "text/markdown",
        "description": "Model card describing intended use, training data, evaluation metrics, and limitations."
    })

    # ---------------------------------------------------------
    # Adding the FAIR4ML Metadata (Task T3.3)
    # ---------------------------------------------------------

    lm_fair4ml = crate.add_file("./outputs/metadata/lm_model_fair4ml.json",
                                dest_path="./outputs/metadata/lm_model_fair4ml.json", properties={
        "name": "FAIR4ML Metadata for Trained Linear Regression model",
        "encodingFormat": "application/json",
        "description": "FAIR4ML-compliant metadata for the trained Linear Regression model."
    })

    lmm_fair4ml = crate.add_file("./outputs/metadata/lmm_model_fair4ml.json", 
                                dest_path="./outputs/metadata/lmm_model_fair4ml.json", properties={
        "name": "FAIR4ML Metadata for Trained Nested Linear Mixed Model",
        "encodingFormat": "application/json",
        "description": "FAIR4ML-compliant metadata for the trained  Nested Linear Mixed Model."
    })

    rf_fair4ml = crate.add_file("./outputs/metadata/rf_model_fair4ml.json",
                                 dest_path="./outputs/metadata/rf_model_fair4ml.json", properties={
        "name": "FAIR4ML Metadata for Trained Random Forest Model",
        "encodingFormat": "application/json",
        "description": "FAIR4ML-compliant metadata for the trained Random Forest model (ranger implementation)."
    })

    models_TUWRD["subjectOf"] = [
        rf_model_card, 
        lm_model_card, 
        lmm_model_card, 
        rf_fair4ml, 
        lm_fair4ml,
        lmm_fair4ml
    ]

    # ---------------------------------------------------------
    # Computational Workflow Context
    # ---------------------------------------------------------
    
    # computational process: define inputs and outputs
    analysis_action = crate.add(ContextEntity(crate, "#ComputationalAnalysis", {
        "@type": "CreateAction",
        "name": "Execution of R modeling scripts calculating Predictive Modeling of Regional GDP based on Wastewater-Based Epidemiology",
        "instrument": r_script,
        "object": [eurostat_gdp, euda_wastewater],
        "result": [output_dataset, models_TUWRD, outputs_TUWRD] 
    }))
    
    crate.root_dataset.append_to("hasPart", [
        eurostat_gdp, 
        euda_wastewater, 
        output_dataset, 
        models_TUWRD,
        outputs_TUWRD,

    ])

    # Save to disk (Writes ro-crate-metadata.json directly into the root directory)
    print("Writing ro-crate-metadata.json metadata footprint out...")

    # Generate the dictionary in memory first
    metadata_dict = crate.metadata.generate()
    
    # Find the metadata descriptor entity and force it to version 1.1
    for entity in metadata_dict["@graph"]:
        if entity["@id"] == "ro-crate-metadata.json":
            entity["conformsTo"] = {"@id": "https://w3id.org/ro/crate/1.1"}
            
    # Safely write to disk without duplicating local files
    with open("ro-crate-metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata_dict, f, indent=4)
        
    print("Success! file compiled.")


if __name__ == "__main__":
    generate_use_case_rocrate()