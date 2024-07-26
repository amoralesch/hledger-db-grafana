create table hledger.assets_classification (
    account varchar(100) not null,
    classification varchar(20) not null
);

create table hledger.balance_to_date (
    date timestamp not null,
    balance numeric not null,
    account varchar(100) not null,
    currency varchar(20) not null
);

create table hledger.daily_delta (
    date timestamp not null,
    balance numeric not null,
    account varchar(100) not null,
    currency varchar(20) not null
);

create table hledger.fx_rate (
    date timestamp not null,
    rate numeric not null,
    currency varchar(20) not null,
    target_currency varchar(20) not null
);

create table hledger.main_commodities (
    currency varchar(20) not null,
    name varchar(100) not null
);
