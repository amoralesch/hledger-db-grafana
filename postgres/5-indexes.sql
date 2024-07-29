create index assets_classification$classification on
hledger.assets_classification (
  classification
);

create index balance_to_date$account on
hledger.balance_to_date (
  account
);

create index fx_rate$target_currency on
hledger.fx_rate (
  target_currency
);

create index main_commodities$currency on
hledger.main_commodities (
  currency
);
