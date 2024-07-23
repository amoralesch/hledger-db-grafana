create table hledger.fx_rate (
    date timestamp not null,
    rate numeric not null,
    currency varchar(20) not null,
    target_currency varchar(20) not null
);

