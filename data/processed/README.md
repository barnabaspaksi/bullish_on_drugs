# Processed Data Guidelines
- Indicate the data source when it is pure according to the naming conventions defined in the README at the root. Not required when data are joined.

# Notes
- Both datasets list some place names in the local language: e.g. Vienna appears as Wien in both datasets.
- Other cities do not match: e.g. Bucharest in the wastewater data is Bucureşti in the GDP dataset. 
- Some cities have different granularity (too): e.g. Athens vs Voreios Tomeas Athinon
- We use a mapping to assign NUTS codes to wastewater data. Some cities share identical NUTS codes with other cities. For simplicity, we only use one of the cities. Alternatively, if scientific accuracy was relevant for the project, we could use weighted means instead.
