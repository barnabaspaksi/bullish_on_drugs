-- 1. THE MAPPING TABLE 
CREATE TABLE city_map_v3 (
    nuts_code VARCHAR(5) NOT NULL,
    city_name VARCHAR(100) NOT NULL,
    PRIMARY KEY (nuts_code),
    UNIQUE (city_name) 
);

-- 2. THE GDP TABLE
CREATE TABLE gdp_data (
    nuts_code VARCHAR(5) NOT NULL,
    ref_year INT NOT NULL,
    gdp_per_cap DECIMAL(15, 2),
    PRIMARY KEY (nuts_code, ref_year),
    FOREIGN KEY (nuts_code) REFERENCES city_map_v3(nuts_code)
);

-- 3. THE WASTEWATER TABLE
CREATE TABLE wastewater_data (
    city_name VARCHAR(100) NOT NULL,
    ref_year INT NOT NULL,
    metabolite_name VARCHAR(100) NOT NULL,
    daily_mean DECIMAL(15, 4),
    PRIMARY KEY (city_name, ref_year, metabolite_name),
    FOREIGN KEY (city_name) REFERENCES city_map_v3(city_name)
);