WITH transactions AS
(
    SELECT
         {{generate_date_id('date')}} AS date_id,
        ticker,
        trade_price,
        amount
    FROM 
        {{ref('stg_transactions')}}
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
        GENERATE_UUID() AS transaction_id,
        date_id,
        t.ticker_id AS ticker_id,
        trade_price,
        amount
    FROM 
        transactions
        JOIN tickers AS t USING (ticker)
)

SELECT * FROM final