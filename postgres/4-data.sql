COPY hledger.main_commodities
FROM '/docker-entrypoint-initdb.d/csv/main_commodities.csv'
DELIMITER ','
CSV HEADER;
