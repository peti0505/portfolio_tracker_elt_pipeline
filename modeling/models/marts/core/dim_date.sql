WITH date_spine AS
(
    {{
        dbt_utils.date_spine(
            datepart="day",
            start_date="CAST('2000-01-01' AS DATE)",
            end_date="CAST('2100-01-01' AS DATE)"
        )
    }}
),

alldates AS
(
    SELECT
        min(date) as partial_min
    FROM
        {{ref('stg_transactions')}}
    UNION ALL
    SELECT
        min(date) as partial_min
    FROM
        {{ref('stg_asset_prices')}}
    UNION ALL
    SELECT
        min(date) as partial_min
    FROM
        {{ref('stg_currency_exchange_rate')}}
),

date_limits AS
(
    SELECT
        MIN(partial_min) AS min_date,
        current_date() as max_date
    FROM 
        alldates
),

limited_dates AS
(
    SELECT
        CAST(ds.date_day AS DATE) AS date
    FROM
        date_spine AS ds
        CROSS JOIN date_limits
    WHERE
        ds.date_day >= min_date
        AND ds.date_day <= max_date
),

final AS
(
    SELECT
        CAST(REPLACE(CAST(date AS STRING),'-','') AS INTEGER) AS date_id,
        date,
        EXTRACT(YEAR FROM date) AS date_year,
        EXTRACT(MONTH FROM date) AS date_month,
        FORMAT_DATE('%B', date) AS date_month_name,
        EXTRACT(DAY FROM date) AS date_day,
        FORMAT_DATE('%A', date) AS date_weekday
    FROM
        limited_dates
)

SELECT * FROM final