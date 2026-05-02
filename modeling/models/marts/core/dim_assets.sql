WITH tickers AS
(
    SELECT DISTINCT
        ticker,
        currency_code
    FROM 
        {{ref('stg_transactions')}}
),

asset_data AS
(
    SELECT
        ticker,
        asset_name,
        exchange_code
    FROM
        {{ref('stg_asset_metadatas')}}
),

final AS
(
    SELECT
        FARM_FINGERPRINT(t.ticker) AS ticker_id,
        t.ticker as ticker,
        asset_name,
        exchange_code,
        currency_code
    FROM
        tickers as t
        JOIN asset_data USING(ticker)
)

SELECT * FROM final