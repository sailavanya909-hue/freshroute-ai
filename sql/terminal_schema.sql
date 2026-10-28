USE freshroute;
CREATE TABLE IF NOT EXISTS terminal_quote (
 quote_id VARCHAR(100) PRIMARY KEY,
 report_date DATE NOT NULL,
 market VARCHAR(100) NOT NULL,
 origin VARCHAR(100) NOT NULL,
 commodity VARCHAR(100) NOT NULL,
 variety VARCHAR(100) NOT NULL,
 grade VARCHAR(100) NOT NULL,
 size_count INT NOT NULL,
 package VARCHAR(100) NOT NULL,
 package_lb DECIMAL(10,3) NOT NULL CHECK(package_lb>0),
 currency CHAR(3) NOT NULL CHECK(currency='USD'),
 low_package DECIMAL(10,4) NOT NULL,
 high_package DECIMAL(10,4) NOT NULL,
 midpoint_package DECIMAL(10,4) NOT NULL,
 midpoint_usd_lb DECIMAL(12,6) NOT NULL,
 source_url VARCHAR(500) NOT NULL,
 source_page INT NOT NULL,
 retrieved_date DATE NOT NULL,
 data_kind VARCHAR(20) NOT NULL CHECK(data_kind='observed'),
 extraction VARCHAR(500) NOT NULL,
 UNIQUE KEY observation (report_date, market, origin, commodity, variety, grade, size_count, package),
 CHECK(low_package>=0 AND high_package>=low_package),
 CHECK(ABS(midpoint_package-(low_package+high_package)/2)<0.0001),
 CHECK(ABS(midpoint_usd_lb-midpoint_package/package_lb)<0.000001)
);
CREATE TABLE IF NOT EXISTS route_assumption (
 market VARCHAR(100) PRIMARY KEY,
 destination VARCHAR(150) NOT NULL,
 freight_usd_lb DECIMAL(12,6) NOT NULL CHECK(freight_usd_lb>=0),
 transit_hours DECIMAL(10,3) NOT NULL CHECK(transit_hours>=0),
 shrink DECIMAL(10,6) NOT NULL CHECK(shrink>=0 AND shrink<1),
 capacity_lb DECIMAL(14,3) NOT NULL CHECK(capacity_lb>0),
 data_kind VARCHAR(20) NOT NULL CHECK(data_kind='assumption')
);
CREATE TABLE IF NOT EXISTS demo_inventory (
 lot_id VARCHAR(100) PRIMARY KEY,
 warehouse VARCHAR(100) NOT NULL,
 quantity_lb DECIMAL(14,3) NOT NULL CHECK(quantity_lb>=0),
 remaining_days INT NOT NULL CHECK(remaining_days>=0),
 purchase_usd_lb DECIMAL(12,6) NOT NULL CHECK(purchase_usd_lb>=0),
 sell_usd_lb DECIMAL(12,6) NOT NULL CHECK(sell_usd_lb>=0),
 data_kind VARCHAR(20) NOT NULL CHECK(data_kind='simulated')
);
CREATE OR REPLACE VIEW terminal_sourcing_base AS
SELECT q.*, r.freight_usd_lb,r.shrink,r.capacity_lb,r.transit_hours,
 (q.midpoint_usd_lb+r.freight_usd_lb)/(1-r.shrink) AS delivered_usd_lb,
 DENSE_RANK() OVER (PARTITION BY q.report_date,q.commodity,q.variety,q.grade,q.origin,q.size_count,q.package
 ORDER BY (q.midpoint_usd_lb+r.freight_usd_lb)/(1-r.shrink)) AS cost_rank
FROM terminal_quote q INNER JOIN route_assumption r ON q.market=r.market;
