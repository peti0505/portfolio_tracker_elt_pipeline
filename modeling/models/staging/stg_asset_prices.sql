WITH staging AS 
(
SELECT
    CAST(LEFT(dates, 10) AS DATE) as dates,
    tickers,
    CAST(REPLACE(CAST(price AS STRING), ',', '.') AS FLOAT64) as price
FROM 
    {{source('portfolio', 'raw_asset_prices')}}
)

SELECT * FROM staging