# Knowledge Graph Generation

This directory contains scripts and resources for generating and populating a financial knowledge graph using Neo4j. The graph integrates all entities from the original FinKG version and additionally incorporates event and news nodes.

## Main Scripts

- [`CoreKG.py`](kg_generation/CoreKG.py):  
  Main script for building the knowledge graph with full metadata.  
  - Key variables to tune:  
    - `self.company_cik_ticker_10kfilename`: Path to the CSV listing companies to include (CIK, ticker, 10K file).
    - `self.csv_event_impacts_path`: Choose which event impacts CSV to use for graph construction.
    - Other paths for news, events, and metadata can be adjusted in the script's `__init__` section.

- [`neo4j_graph.py`](kg_generation/neo4j_graph.py):  
  Core Neo4j interface and utility class for all graph operations.

## Additional Scripts

- [`add_events_to_neo.py`](kg_generation/add_events_to_neo.py)  
- [`start_neo4j.py`](kg_generation/start_neo4j.py)  

These provide fast deployment using only triple files (CSV format) without loading metadata. Use this for quick imports if you do not need the full metadata features.

## Data & Resources

- `csvTriples/`:  
  Contains CSV files with subject-predicate-object triples for companies, events, news, etc. You can also generate these triples using the `createTriplesCSV()` method in the main code. Note that for the triples containing News and Events you will have to use the [`event_detection_analysis.ipynb`](event_detection_analysis.ipynb) notebook in the `event_detection` section.

- `data/`:  
  Contains supporting data files, including news/event metadata and mapping tables and csv file with seed companies for populating the graph.

  **Example format for company CSV:**  
  ```
  cik,ticker,10k_filename
  0000320193,AAPL,0000320193-21-000010.txt
  0000789019,MSFT,0000789019-21-000065.txt
  ```
  The main graph code processes and adds companies listed in this CSV.

## Environment Setup

1. **Create and activate a Python environment:**
   ```sh
   python -m venv venv
   venv\Scripts\activate   # On Windows
   # Or: source venv/bin/activate   # On Linux/Mac
   ```

2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

3. **Ensure Neo4j is running locally or update connection settings in `neo4j_graph.py` as needed.**

> **Note:**  
> You can modify the connection variables (`user`, `password`, `host_name`, `port`, `database`) directly in [`neo4j_graph.py`](kg_generation/neo4j_graph.py) inside the `__init__` method of the `Neo4jGraph` class.  
> Adjust these values to match your Neo4j configuration.

## Usage

1. **Full Graph Construction:**  
   Run [`CoreKG.py`](kg_generation/CoreKG.py) to build the complete graph with metadata.

   ```sh
   python CoreKG.py
   ```

2. **Quick Triple Import:**  
   Use the additional scripts for fast import from CSV triples (no metadata).
