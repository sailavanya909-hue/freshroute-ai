CREATE DATABASE IF NOT EXISTS freshroute;
USE freshroute;

CREATE TABLE IF NOT EXISTS market_price (
 price_date DATE NOT NULL,
 state VARCHAR(100) NOT NULL,
 district VARCHAR(100) NOT NULL,
 market VARCHAR(150) NOT NULL,
 commodity VARCHAR(100) NOT NULL,
 variety VARCHAR(100) NOT NULL,
 grade VARCHAR(100) NOT NULL,
 min_inr_kg DECIMAL(12,4) NOT NULL,
 modal_inr_kg DECIMAL(12,4) NOT NULL,
 max_inr_kg DECIMAL(12,4) NOT NULL,
 source_url VARCHAR(500) NOT NULL,
 retrieved_at DATETIME NOT NULL,
 PRIMARY KEY(price_date,state,district,market,commodity,variety,grade),
 CHECK(min_inr_kg >= 0 AND min_inr_kg <= modal_inr_kg AND modal_inr_kg <= max_inr_kg)
);

CREATE TABLE IF NOT EXISTS inventory_lot (
 lot_id BIGINT PRIMARY KEY,
 commodity VARCHAR(100) NOT NULL,
 variety VARCHAR(100) NOT NULL,
 grade VARCHAR(100) NOT NULL,
 warehouse VARCHAR(100) NOT NULL,
 received_date DATE NOT NULL,
 expiry_date DATE NOT NULL,
 quantity_kg DECIMAL(14,3) NOT NULL CHECK(quantity_kg >= 0),
 purchase_inr_kg DECIMAL(12,4) NOT NULL CHECK(purchase_inr_kg >= 0),
 data_kind ENUM('actual','assumption') NOT NULL,
 CHECK(expiry_date >= received_date)
);

CREATE TABLE IF NOT EXISTS route_input (
 route_id BIGINT PRIMARY KEY,
 origin VARCHAR(150) NOT NULL,
 destination VARCHAR(150) NOT NULL,
 transit_hours DECIMAL(10,2) NOT NULL CHECK(transit_hours >= 0),
 freight_inr_kg DECIMAL(12,4) NOT NULL CHECK(freight_inr_kg >= 0),
 capacity_kg DECIMAL(14,3) NOT NULL CHECK(capacity_kg > 0),
 quoted_date DATE NOT NULL,
 data_kind ENUM('actual','assumption') NOT NULL
);

CREATE TABLE IF NOT EXISTS scenario_result (
 scenario_id BIGINT PRIMARY KEY,
 scenario_name VARCHAR(100) NOT NULL,
 evaluated_at DATETIME NOT NULL,
 evidence_date DATE NOT NULL,
 commodity VARCHAR(100) NOT NULL,
 market VARCHAR(150) NOT NULL,
 quantity_kg DECIMAL(14,3) NOT NULL CHECK(quantity_kg > 0),
 buy_inr_kg DECIMAL(12,4) NOT NULL CHECK(buy_inr_kg >= 0),
 sell_inr_kg DECIMAL(12,4) NOT NULL CHECK(sell_inr_kg >= 0),
 freight_inr_kg DECIMAL(12,4) NOT NULL CHECK(freight_inr_kg >= 0),
 spoilage_fraction DECIMAL(8,6) NOT NULL CHECK(spoilage_fraction >= 0 AND spoilage_fraction < 1),
 assumption_note TEXT NOT NULL
);

CREATE OR REPLACE VIEW scenario_economics AS
SELECT *,
 quantity_kg * (1-spoilage_fraction) AS saleable_kg,
 quantity_kg * (buy_inr_kg + freight_inr_kg) AS total_cost_inr,
 quantity_kg * (1-spoilage_fraction) * sell_inr_kg AS modeled_revenue_inr,
 quantity_kg * ((1-spoilage_fraction)*sell_inr_kg-buy_inr_kg-freight_inr_kg) AS modeled_contribution_inr
FROM scenario_result;

-- Compare like-for-like observations, not markets with different varieties/grades.
CREATE OR REPLACE VIEW market_comparison AS
SELECT *, modal_inr_kg - MIN(modal_inr_kg) OVER (
 PARTITION BY price_date, state, commodity, variety, grade
) AS premium_to_lowest_inr_kg
FROM market_price;
