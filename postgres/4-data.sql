COPY hledger.assets_classification
FROM '/docker-entrypoint-initdb.d/csv/assets_classification.csv'
DELIMITER ','
CSV HEADER;

COPY hledger.main_commodities
FROM '/docker-entrypoint-initdb.d/csv/main_commodities.csv'
DELIMITER ','
CSV HEADER;
