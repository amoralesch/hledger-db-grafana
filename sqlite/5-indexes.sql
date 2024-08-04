create index assets_classification$classification on
assets_classification (
  classification
);

create index balance_to_date$account on
balance_to_date (
  account
);

create index fx_rate$target_currency on
fx_rate (
  target_currency
);

create index main_commodities$currency on
main_commodities (
  currency
);
