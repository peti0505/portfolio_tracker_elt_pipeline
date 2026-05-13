import logging
import config as c
import extraction as e
import loading as l

logger = logging.getLogger(__name__)


def main() -> None:

    logger.info("_" * 30)
    logger.info("Portfolio loading started")
    conf = c.get_conf()
    df_transactions = e.get_googlesheet_transactions(conf)
    switch = l.transactions_to_gbq(df_transactions, conf)
    l.clean_google_sheets(switch, conf)
    tickers = e.gbq_get_tickers(conf)
    all_tickers = e.gbq_get_all_tickers(conf)
    currencies = e.gbq_get_currencies(conf)
    asset_metadatas = e.api_get_asset_metadata(all_tickers, conf)
    asset_prices = e.api_get_asset_price(tickers, conf)
    currency_rates = e.api_get_currency_rate(currencies)
    l.asset_metadata_to_gbq(asset_metadatas, conf)
    l.asset_prices_to_gbq(asset_prices, conf)
    l.currency_rates_to_gbq(currency_rates, conf)
    logger.info("Portfolio loading finished")
    logger.info("_" * 30)


if __name__ == "__main__":
    main()
