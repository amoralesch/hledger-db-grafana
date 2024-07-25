create view hledger.average_daily_expenses as
select
    a.date,
    b.target_currency as currency,
    (
        sum(a.balance * b.rate) -
        LAG(sum(a.balance * b.rate), 365) OVER (PARTITION BY a.account, b.target_currency ORDER BY a.date)
    ) /
    (
        EXTRACT(epoch FROM
            a.date -
            LAG(a.date, 365) OVER (PARTITION BY a.account, b.target_currency ORDER BY a.date)
        ) / 86400
    ) as daily_expense
from hledger.balance_to_date a
join hledger.fx_rate b on
    a.date = b.date and
    a.currency = b.currency
join hledger.main_commodities c on
    b.target_currency = c.currency
where
    a.account = 'Expenses'
group by
    a.date,
    a.account,
    b.target_currency;

create view hledger.average_daily_income as
select
    a.date,
    b.target_currency as currency,
    (
        sum(a.balance * b.rate) -
        LAG(sum(a.balance * b.rate), 365) OVER (PARTITION BY a.account, b.target_currency ORDER BY a.date)
    ) /
    (
        EXTRACT(epoch FROM
            a.date -
            LAG(a.date, 365) OVER (PARTITION BY a.account, b.target_currency ORDER BY a.date)
        ) / 86400
    ) as daily_income
from hledger.balance_to_date a
join hledger.fx_rate b on
    a.date = b.date and
    a.currency = b.currency
join hledger.main_commodities c on
    b.target_currency = c.currency
where
    a.account = 'Income'
group by
    a.date,
    a.account,
    b.target_currency;

create view hledger.average_daily_savings as
select
    a.date,
    b.target_currency as currency,
    (
        sum(a.balance * b.rate) -
        LAG(sum(a.balance * b.rate), 365) OVER (PARTITION BY a.account, b.target_currency ORDER BY a.date)
    ) /
    (
        EXTRACT(epoch FROM
            a.date -
            LAG(a.date, 365) OVER (PARTITION BY a.account, b.target_currency ORDER BY a.date)
        ) / 86400
    ) as daily_savings
from hledger.balance_to_date a
join hledger.fx_rate b on
    a.date = b.date and
    a.currency = b.currency
join hledger.main_commodities c on
    b.target_currency = c.currency
join hledger.assets_classification d on
    a.account = d.account
where
    d.classification = 'Savings'
group by
    a.date,
    a.account,
    b.target_currency;

create view hledger.balance_to_date_converted as
select
    a.date,
    sum(a.balance * b.rate) as balance,
    a.account,
    b.target_currency as currency
from hledger.balance_to_date a
join hledger.fx_rate b on
    a.date = b.date and
    a.currency = b.currency
group by
    a.date,
    a.account,
    b.target_currency;

create view hledger.net_worth as
select
    date,
    currency,
    sum(balance) as net_worth
from hledger.balance_to_date_converted
where
    account in ('Assets', 'Liabilities', 'Transfer')
group by
    date,
    currency;
