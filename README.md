# Portfolio Tracker Pipeline
Automated end-to-end ELT data pipeline for tracking an EUR based portfolio value, separating asset and FX yield and insights over time.

## Business problem
Tracking an investment portfolio manually without insights can be troublesome and error-prone. This project wants to eliminate these problems by needing only the new asset transactions loaded into a Google Sheet, then using a **Modern Data Stack** extract, load and transform the data before visualizing it.

**Explore the Interactive dbt Data Lineage and Documentation:**

## Architecture and Dataflow

(workflow img)

## Tech Stack

* **Data Sources**: Google Sheets API (gspread), Tiingo API, Frankfurter API
* **Extraction and Loading**: Python -> Pandas, Pandas_gbq, requests, comprehensive logging and error-handling
* **Data Warehouse**: Google BigQuery -> Cloud based DWH
* **Transformation and Modeling**: dbt -> Making Star Schema, jinja, data quality tests, data documentation
* **Containerization**: Docker -> Separating Extraction-Load, Modeling and Airflow into Docker containers
* **Orchestration**: Apache Airflow -> Orchestrating the Docker containers to run the pipeline, PostgreSQL backend
* **Visualization**: Power BI -> Dax measures, bookmarks

## Data Model

(db star schema img)

This Star Schema is the gold level of the **Medallion Structure**. It gets build from the staging tables which is the silver level. The analytics layer is built from this core schema. <br>
**For an interactive documentation on the modeling and lineage visit:** (dbt doc site link)

## Project Structure
```hb
(filetree)
```

### Pipeline features
1. **Data extraction** <br>
The main.py starts the process. The new transactions from the **Google Sheets** get extracted and loaded into **BigQuery**. Only after that will the asset price and FX rate fetching begin. First it fetches the active asset tickers and currencies, only these prices will be fetched from the APIs for **optimization**.

2. **Data Loading** <br>
Every table get loaded into **Google BigQuery** as **raw tables** for future modeling.  If the transaction loading was successfu the Google Sheets transactions gets cleared  to maintain **idempotency**.

3. **Data Modeling** <br>
The staging level is materialized as views so it refreshes instantly. The core **Star Schema** contains **forward filling** for asset prices and FX rates to fill the days where there were no data for it with the **last known price**. 

4. **Data testing** <br>
Data quality tests are being done on every stage of the data in BigQuery. **Generic and singular tests** as well with the help of dbt. This assures that there **won't be any false information downstream**.

5. **Visualization** <br>
The visualization contains the following insights: <br>
**Total value over time** - > The cumulative value of the portfolio over time. <br>
**Top and bottom performers** -> List of the assets that had the highest and lowest earning for the portfolio.
**Asset allocation** -> A treemap to see individual asset earnings and exposure. <br>
**KPIs** -> The asset and FX earning are separated.

6. **Orchestration** <br>
The Airflow gets all the environment variables and the Google Cloud Platform service key to pass on to the containers. The Airflow runs in a container as well, it executes the DAG using the host **Docker Socket**. <br>
If needed the pipeline can be started with the docker-compose aswell, but only the Airflow has 
scheduled running.

**Note: The portfolio contains fictional transactions, it doesn't resemble a real portfolio.**

## Visualization

(visualization img)

# How to Run

### Prerequisites
* **Docker** and **Docker Compose**.
* A GCP project with a BigQuery dataset.
* A GCP Service account .json key with admin privileges.
* API token for **Tiingo**

### Setup
1. **Clone the repository**
```bash
   git clone https://github.com/peti0505/portfolio_tracker_elt_pipeline.git
   cd portfolio_tracking
```

2. **Configure environment variables** <br>
Open the .envEXAMPLE file, write your environment variables according to the instructions then delete the .EXAMPLE from the file name.

3. **Add GCP credentials** <br>
Paste the Google Cloud Platform service key for the project into the gcp_keyEXAMPLE.json file or replace the file. Delete the .EXAMPLE from the file name.

4. **Build the images**
```bash
docker compose --profile portfolio_pipeline build
```
5. **Starting the pipeline** <br>
* If you want to start it with Airflow:
    - ```bash
        docker compose up -d
        ```
    - Navigate to http://localhost:8080 in your browser.
    - Log in to Airflow (default credentials: airflow airflow)
    - Unpause or trigger the dag to execute the pipeline

* If you want to start it with Docker Compose without scheduling:
    - ```bash
        docker compose --profile portfolio_pipeline up
        ```
