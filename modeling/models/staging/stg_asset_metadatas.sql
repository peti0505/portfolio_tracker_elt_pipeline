WITH staging AS
(
SELECT DISTINCT
    UPPER(TRIM(tickers)) AS ticker,
    asset_name,
    UPPER(TRIM(exchange_code)) AS exchange_code
FROM
    {{source('portfolio', 'raw_asset_metadatas')}}
)

SELECT * FROM staging