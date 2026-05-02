WITH prices AS 
(
    SELECT
        {{generate_date_id('date')}} AS date_id,
        ticker,
        price AS asset_price
    FROM
        {{ref('stg_asset_prices')}}
),

tickers AS
(
    SELECT
        ticker_id,
        ticker
    FROM
        {{ref('dim_assets')}}
),

final AS
(
    SELECT
        GENERATE_UUID() AS asset_price_id,
        date_id,
        t.ticker_id AS ticker_id,
        asset_price
    FROM
        prices
        JOIN tickers AS t USING (ticker)
)

SELECT * FROM final