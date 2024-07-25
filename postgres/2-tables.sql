create table hledger.balance_to_date (
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
