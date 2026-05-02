WITH currency_rates AS
(
    SELECT
        GENERATE_UUID() AS currency_rate_id,
        {{generate_date_id('date')}} AS date_id,
        currency_code,
        rate AS currency_rate
    FROM
        {{ref('stg_currency_exchange_price')}}
)

SELECT * FROM currency_rates