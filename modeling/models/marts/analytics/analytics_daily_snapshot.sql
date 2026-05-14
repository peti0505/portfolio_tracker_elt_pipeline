WITH daily_asset_prices AS
(
    SELECT
        date_id,
        ticker_id,
        asset_price,
    FROM 
        {{ref('fact_asset_prices')}}
),

currencies AS
(
    SELECT
        date_id,
        currency_code,
        currency_rate,
    FROM
        {{ref('fact_currency_exchange_rate')}}
),

transactions AS
(
    SELECT
        tr.date_id,
        ticker_id,
        SUM(amount) as daily_amount,
        SUM(trade_price*amount) AS daily_cost,
        SUM(trade_price*amount/currency_rate) AS daily_cost_base
    FROM
        {{ref('fact_transactions')}} as tr
        JOIN {{ref('dim_assets')}} USING (ticker_id)
        JOIN currencies USING (date_id, currency_code)
    GROUP BY 
        1,2
),

ticker_datas AS
(
    SELECT
        date_id,
        ticker_id,
        currency_code,
        asset_price,
        --The daily sums can't be null, if it is 0 it should still be kept in record.
        COALESCE(daily_amount, 0) AS daily_amount,
        COALESCE(daily_cost, 0) AS daily_cost,
        COALESCE(daily_cost_base, 0) AS daily_cost_base
    FROM
        daily_asset_prices
        JOIN {{ref('dim_assets')}} USING (ticker_id)
        LEFT JOIN transactions USING(date_id, ticker_id)
),

rolling_totals AS
(
    SELECT
        date_id,
        ticker_id,
        --Rolling sum to see amount, price, base price and cost day by day. The yield gets calculated from this.
        SUM(daily_amount) OVER(PARTITION BY ticker_id ORDER BY date_id) AS cumulative_amount,
        COALESCE((SUM(daily_amount) OVER(PARTITION BY ticker_id ORDER BY date_id))*asset_price, 0) AS market_value,
        COALESCE((SUM(daily_amount) OVER(PARTITION BY ticker_id ORDER BY date_id))*asset_price/currency_rate, 0) AS market_value_base,
        SUM(daily_cost) OVER(PARTITION BY ticker_id ORDER BY date_id) AS cumulative_cost,
        SUM(daily_cost_base) OVER(PARTITION BY ticker_id ORDER BY date_id) AS cumulative_cost_base
    FROM
        ticker_datas
        JOIN currencies
        USING (date_id, currency_code)
),

final AS
(
    SELECT
        date_id,
        ticker_id,
        cumulative_amount,
        market_value,
        market_value_base,
        cumulative_cost,
        cumulative_cost_base,
        --Calculating the yield on the cost's currency rate to prepare FX yield and asset yield separation.
        COALESCE(market_value*SAFE_DIVIDE(cumulative_cost_base,cumulative_cost),0) AS market_value_on_cost_currency,
    FROM
        rolling_totals
)


SELECT * FROM final