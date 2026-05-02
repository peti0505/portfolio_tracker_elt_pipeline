WITH staging AS 
(
SELECT DISTINCT
    CAST(LEFT(dates, 10) AS DATE) AS date,
    UPPER(tickers) AS ticker,
    CAST(REPLACE(CAST(price AS STRING), ',', '.') AS FLOAT64) AS price
FROM 
    {{source('portfolio', 'raw_asset_prices')}}
)

SELECT * FROM staging