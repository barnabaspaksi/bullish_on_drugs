-- 1. THE MAPPING TABLE 
CREATE TABLE city_map (
    nuts_code VARCHAR(5) NOT NULL,
    city_name VARCHAR(100) NOT NULL,
    PRIMARY KEY (nuts_code),
    UNIQUE (city_name) 
);

-- 2. THE GDP TABLE
CREATE TABLE gdp_data (
    nuts_code VARCHAR(5) NOT NULL,
    ref_year INT NOT NULL,
    gdp DECIMAL(30),
    currency VARCHAR(10),
    PRIMARY KEY (nuts_code, ref_year),
    CONSTRAINT fk_gdp_data_0 FOREIGN KEY (nuts_code) REFERENCES city_map(nuts_code)
);

-- 3. THE WASTEWATER TABLE
CREATE TABLE wastewater_data (
    city_name VARCHAR(100) NOT NULL,
    ref_year INT NOT NULL,
    metabolite_name VARCHAR(100) NOT NULL,
    daily_mean_concentration DECIMAL(15),
    PRIMARY KEY (city_name, ref_year, metabolite_name),
    CONSTRAINT fk_wastewater_data_0 FOREIGN KEY (city_name) REFERENCES city_map(city_name)
);