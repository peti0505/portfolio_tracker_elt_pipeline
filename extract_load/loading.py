import pandas as pd
import pandas_gbq
import gspread
import logging

logger = logging.getLogger(__name__)


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
