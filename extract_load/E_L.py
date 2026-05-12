import requests
from dotenv import load_dotenv
import os
import pandas as pd
import gspread
import pandas_gbq
from google.oauth2 import service_account
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatting = logging.Formatter(
    "%(asctime)s-%(levelname)s-%(name)s-%(funcName)s-%(message)s"
)
file = logging.FileHandler("dataloading.log")
file.setFormatter(formatting)
logger.addHandler(file)


def get_conf() -> dict:
    """
    Fetch the variables from .env file.

    Returns:
        dict: Containing the api token, GBQ project IDs and credentials doc.
    """

    try:
        load_dotenv()

        conf = {
            "tiingo_api_token": os.environ.get("tiingo_api_token"),
            "json_file_path": os.environ.get("gc_service_account_json_path"),
            "credentials": service_account.Credentials.from_service_account_file(
                os.environ.get("gc_service_account_json_path")
            ),
            "project": os.environ.get("project_id"),
            "dataset": os.environ.get("dataset_name"),
            "transactions_table": os.environ.get("dataset_name")
            + "."
            + "raw_transactions",
        }

    except:
        logger.exception("Couldn't read .env file.")

        raise

    else:
        logger.info("Config read successfully from .env file.")

        return conf


def get_googlesheet_transactions(conf: dict) -> pd.DataFrame:
    """
    Fetch the batch of transactions from Google Sheets.

    Args:
        conf (dict): The dict containing the configurating data and authentications.

    Returns:
        pd.DataFrame: Contains the transactions, if no transactions were extracted, it returns an empty DataFrame.
    """

    try:
        gc = gspread.service_account(filename=conf["json_file_path"])
        sh = gc.open("portfolio_transactions")
        worksheet = sh.worksheet("Transactions")

        transaction_dict = worksheet.get_all_records()
        df_transactions = pd.DataFrame(transaction_dict)

    except:
        logger.exception("Couldn't read transactions from google sheets.")

        df_transactions = pd.DataFrame()

        return df_transactions

    else:

        if df_transactions.empty:
            logger.info("The transactions sheet was empty.")

        else:
            logger.info("Transactions read successfully.")

        return df_transactions


def transactions_to_gbq(transactions: pd.DataFrame, conf: dict) -> bool:
    """
    Load the transactions into Google BigQuery.

    Args:
        transactions (pd.DataFrame):  Contains the transactions that need to be loaded.
        conf (dict): The dict containing the configurating data and authentications.

    Returns:
        bool: True if the load was successful, False if the DataFrame was empty or the load failed.
    """

    if transactions.empty:
        logger.info("Couldn't load transactions, transactions were empty.")

        return False

    else:
        try:
            pandas_gbq.to_gbq(
                transactions,
                conf["transactions_table"],
                project_id=conf["project"],
                if_exists="append",
                credentials=conf["credentials"],
            )

        except:
            logger.exception("Couldn't load transactions into Google BigQuery.")

            return False

        else:
            logger.info("Transactions loaded into Google BigQuery successfully.")

            return True


def clean_google_sheets(switch: bool, conf: dict) -> None:
    """
    Cleans the Google Sheet from the loaded transactions.

    Args:
        switch (bool): True if the transactions were loaded correctly and the deleting can commence or False if the deleting should be aborted.
        conf (dict): The dict containing the configurating data and authentications.
    """

    if switch:
        try:
            gc = gspread.service_account(filename=conf["json_file_path"])
            sh = gc.open("portfolio_transactions")
            worksheet = sh.worksheet("Transactions")

            # Assumes a batch of transactions contains 999 transactions max with 5 columns each.
            worksheet.batch_clear(["A2:E1000"])

        except:
            logger.exception("Couldn't clear Google Sheets transactions")

        else:
            logger.info("Google Sheets cleaned successfully.")

    else:
        logger.info(
            "Couldn't clear the sheet, no transactions were loaded to Google BigQuery."
        )


def gbq_get_tickers(conf: dict) -> list:
    """
    Fetch all the currently active tickers from the transactions table.

    Args:
        conf (dict): The dict containing the configurating data and authentications.

    Returns:
        list: Containing the currently active unique tickers.
    """

    try:
        # Filter out closed positions for API ooptimization.
        sql = f"""
        WITH ticker_total AS
        (
        SELECT
        Ticker,
        sum(`Amount + for buy - for sell`) as Current_total
        FROM {conf["transactions_table"]}
        GROUP BY 1
        HAVING sum(`Amount + for buy - for sell`) > 0
        )
        SELECT
        Ticker
        FROM
        ticker_total
        """

        df_tickers = pandas_gbq.read_gbq(
            sql, project_id=conf["project"], credentials=conf["credentials"]
        )

        tickers = df_tickers["Ticker"].to_list()

    except:
        logger.exception("Couldn't fetch the active tickers from Google BigQuery.")

        raise

    else:
        logger.info("Currently active tickers fetched successfully.")

        return tickers


def gbq_get_all_tickers(conf: dict) -> list:
    """
    Fetch all the tickers which were in the transactions list at any point in time.

    Args:
        conf (dict): The dict containing the configurating data and authentications.

    Returns:
        list: Containing all the unique tickers.
    """

    try:
        sql = f"""
        SELECT
        Ticker
        FROM {conf["transactions_table"]}
        GROUP BY 1
        """

        df_tickers = pandas_gbq.read_gbq(
            sql, project_id=conf["project"], credentials=conf["credentials"]
        )

        tickers = df_tickers["Ticker"].to_list()

    except:
        logger.exception("Couldn't fetch all time tickers from Google BigQuery.")

        raise

    else:
        logger.info("All time tickers fetched successfully")

        return tickers


def gbq_get_currencies(conf: dict) -> list:
    """
    Fetch all the active currency codes in the transactions table.

    Args:
        conf (dict): The dict containing the configurating data and authentications.

    Returns:
        list: Containing the currently active unique currencies.
    """

    try:
        # Filter out closed positions for API optimization.
        # Exclude EUR currency because it is the base currency of the portfolio.
        sql = f"""
        WITH ticker_total AS
        (
        SELECT
        Ticker,
        `Currency code`,
        sum(`Amount + for buy - for sell`) as Current_total
        FROM {conf["transactions_table"]}
        GROUP BY 1, 2
        HAVING sum(`Amount + for buy - for sell`) > 0
        )
        SELECT DISTINCT
        `Currency code`
        FROM
        ticker_total
        WHERE `Currency code` != 'EUR'
        """

        df_currencies = pandas_gbq.read_gbq(
            sql, project_id=conf["project"], credentials=conf["credentials"]
        )

        currencies = df_currencies["Currency code"].to_list()

    except:
        logger.exception("Couldn't fetch unique currencies from Google BigQuery.")

        raise

    else:
        logger.info("Unique currencies fetched successfully.")

        return currencies


def api_get_asset_metadata(asset_tickers: list, conf: dict) -> pd.DataFrame:
    """
    Fetch the ticker metadata from the Tiingo API.

    Args:
        asset_tickers (list): Containing the tickers that we need metadata for.
        conf (dict): The dict containing the configurating data and authentications.

    Returns:
        pd.DataFrame: Containing the ticker, the full name of the asset and the exchange code it is traded on.
    """

    try:
        metadata_list = []
        # Iterating because Tiingo only supports singular ticker requests.
        for ticker in asset_tickers:

            headers = {
                "Content-Type": "application/json",
                "Authorization": conf["tiingo_api_token"],
            }

            response = requests.get(
                f"https://api.tiingo.com/tiingo/daily/{ticker}",
                headers=headers,
                timeout=10,
            )

            r = response.json()
            metadata = {
                "tickers": ticker,
                "asset_name": r["name"],
                "exchange_code": r["exchangeCode"],
            }
            metadata_list.append(metadata)

        df_metadata = pd.DataFrame(metadata_list)

    except:
        logger.exception("Couldn't fetch API asset metadata.")

        raise

    else:
        logger.info("API asset metadata fetched successfully.")

        return df_metadata


def api_get_asset_price(asset_tickers: list, conf: dict) -> pd.DataFrame:
    """
    Fetch the ticker prices from the Tiingo API.

    Args:
        asset_tickers (list): Containing the tickers that we need prices for.
        conf (dict): The dict containing the configurating data and authentications.

    Returns:
        pd.DataFrame: Containing the date of the price, the ticker and the price for that ticker.
    """

    try:
        price_list = []
        # Iterating because Tiingo only supports singular ticker requests.
        for ticker in asset_tickers:

            headers = {
                "Content-Type": "application/json",
                "Authorization": conf["tiingo_api_token"],
            }

            response = requests.get(
                f"https://api.tiingo.com/tiingo/daily/{ticker}/prices",
                headers=headers,
                timeout=10,
            )

            r = response.json()
            price = {
                "dates": r[0]["date"],
                "tickers": ticker,
                "price": r[0]["adjClose"],
            }
            price_list.append(price)

        df_prices = pd.DataFrame(price_list)

    except:
        logger.exception("Couldn't fetch API asset prices.")

        raise

    else:
        logger.info("API asset prices fetched successfully.")

        return df_prices


def api_get_currency_rate(currency_list: list) -> pd.DataFrame:
    """
    Fetch the currency rates from the Frankfurter API.

    Args:
        currency_list (list): Containing the currencies that we need the rates for with EUR base.

    Returns:
        pd.DataFrame: Containing the date of the exchange rate, the currency code and the rate for that currency with EUR base.
    """

    try:
        # The Frankfurter API supports bulk requests, we dont need to iterate.
        currency_list = ",".join(currency_list)

        response = requests.get(
            f"https://api.frankfurter.dev/v2/rates?quotes={currency_list}", timeout=10
        )
        r = response.json()

        currencies = []
        for i in r:
            currencies_row = {
                "dates": i["date"],
                "currency_code": i["quote"],
                "rate": i["rate"],
            }
            currencies.append(currencies_row)

        df_currencies = pd.DataFrame(currencies)

    except:
        logger.exception("Couldn't fetch API currency rates.")

        raise

    else:
        logger.info("API currency rates fetched successfully.")

        return df_currencies


def asset_metadata_to_gbq(metadata: pd.DataFrame, conf: dict) -> None:
    """
    Load asset metadata table into Google BigQuery.

    Args:
        metadata (pd.DataFrame): Containing the asset metadata.
        conf (dict): The dict containing the configurating data and authentications.
    """

    try:
        table = conf["dataset"] + "." + "raw_asset_metadatas"
        pandas_gbq.to_gbq(
            metadata,
            table,
            project_id=conf["project"],
            if_exists="replace",  # Using replace so the table keeps its dimension table attribute
            credentials=conf["credentials"],
        )

    except:
        logger.exception("Couldn't load asset metadata into Google BigQuery.")

        raise

    else:
        logger.info("Asset metadata loaded into Google BigQuery successfully.")


def asset_prices_to_gbq(prices: pd.DataFrame, conf: dict) -> None:
    """
    Load asset prices table into Google BigQuery.

    Args:
        prices (pd.DataFrame): Containing the asset prices.
        conf (dict): The dict containing the configurating data and authentications.
    """

    try:
        table = conf["dataset"] + "." + "raw_asset_prices"
        pandas_gbq.to_gbq(
            prices,
            table,
            project_id=conf["project"],
            if_exists="append",  # Using append so the table keeps the historcial prices.
            credentials=conf["credentials"],
        )

    except:
        logger.exception("Couldn't load asset prices into Google BigQuery.")

        raise

    else:
        logger.info("Asset prices loaded into Google BigQuery successfully.")


def currency_rates_to_gbq(currencies: pd.DataFrame, conf: dict) -> None:
    """
    Load currency rates on EUR base table into Google BigQuery.

    Args:
        currencies (pd.DataFrame): Containing the currency exchange rates on EUR base.
        conf (dict): The dict containing the configurating data and authentications.
    """

    try:
        table = conf["dataset"] + "." + "raw_currency_exchange_price"
        pandas_gbq.to_gbq(
            currencies,
            table,
            project_id=conf["project"],
            if_exists="append",  # Using append so the table keeps the historcial prices.
            credentials=conf["credentials"],
        )

    except:
        logger.exception("Couldn't load currency rates into Google BigQuery.")

        raise

    else:
        logger.info("Currency rates loaded into Google BigQuery successfully.")


def main() -> None:

    conf = get_conf()
    df_transactions = get_googlesheet_transactions(conf)
    switch = transactions_to_gbq(df_transactions, conf)
    clean_google_sheets(switch, conf)
    tickers = gbq_get_tickers(conf)
    all_tickers = gbq_get_all_tickers(conf)
    currencies = gbq_get_currencies(conf)
    asset_metadatas = api_get_asset_metadata(all_tickers, conf)
    asset_prices = api_get_asset_price(tickers, conf)
    currency_rates = api_get_currency_rate(currencies)
    asset_metadata_to_gbq(asset_metadatas, conf)
    asset_prices_to_gbq(asset_prices, conf)
    currency_rates_to_gbq(currency_rates, conf)


if __name__ == "__main__":
    main()
