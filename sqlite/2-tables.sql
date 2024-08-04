create table assets_classification (
    account varchar(100) not null,
    classification varchar(20) not null
);

create table balance_to_date (
    date timestamp not null,
    balance numeric not null,
    account varchar(100) not null,
    currency varchar(20) not null
);

create table daily_delta (
    date timestamp not null,
    balance numeric not null,
    account varchar(100) not null,
    currency varchar(20) not null
);

create table fx_rate (
    date timestamp not null,
    rate numeric not null,
    currency varchar(20) not null,
    target_currency varchar(20) not null
);

create table main_commodities (
    currency varchar(20) not null,
    name varchar(100) not null
);
