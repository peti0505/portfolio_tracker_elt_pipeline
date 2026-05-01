WITH staging AS
(
SELECT 
    CAST(LEFT(REPLACE(`Date YYYY-MM-DD`,'.','-'),10) as DATE) as date,
    Ticker as ticker,
    `Trade price use dot for decimal` as trade_price,
    `Currency code` as currency_code,
    `Amount + for buy - for sell` as amount
FROM 
    {{source('portfolio', 'raw_transactions')}}
)

SELECT * FROM staging