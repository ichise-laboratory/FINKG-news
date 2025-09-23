# Event Detection

In this module we process a set of news articles and detect events within them using a LLM. Results are saved for further analysis and knowledge graph generation.

---

## Table of Contents

- [Setup](#setup)
- [Model Selection](#model-selection)
- [Configuration](#configuration)
- [Running the Script](#running-the-script)
- [Monitoring Progress](#monitoring-progress)
- [Output Files](#output-files)
- [Data Files](#data-files)
- [Notebooks](#notebooks)

---

## Setup

1. **Create a virtual environment**  
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install requirements**  
   ```sh
   pip install -r requirements.txt
   ```

3. **Install Ollama**  
   Download and install Ollama from [https://ollama.com/download](https://ollama.com/download).

---

## Model Selection

By default, the script uses the `llama3:70b` model.  
To download a model with Ollama, run:
```sh
ollama pull llama3:70b
```
To use a different model, change the `llm_model` variable in [`run_event_detection.py`](run_event_detection.py).

See available models at [https://ollama.com/library](https://ollama.com/library).

---

## Configuration

You can tune the following variables in [`run_event_detection.py`](run_event_detection.py):

```python
news_csv = "filtered_news/filtered_news_with_keywords_v2.csv"  # News to process
events_path = "event_jsons/new_events.json"                    # Events to spot
experiment_name = f"output_detection/experiment_{timestamp}.jsonl"  # Output file
DEBUG = True
event_chunk_size = 20      # Events per system prompt
token_limit = 2600         # Max tokens for model input
llm_model = "llama3:70b"   # Model name
```

---

## Running the Script

Run the event detection in the background (recommended for long processing):

```sh
nohup python run_event_detection.py &
```

---

For monitoring the progress you can:

- **Check if the script is running:**
  ```sh
  ps aux | grep run_event_detection.py
  ```
- **View output log:**
  ```sh
  tail -f nohup.out
  ```
- **Results:**  
  Output files are saved in the [`output_detection`](output_detection/) folder.

---

## Data Files

- [`event_jsons/`](event_jsons/)
  - `dict_wiki_timelines5_geo_country_event.json`: This is the original set of news, without preprocessing (It is used in [`event_classification.ipynb`](event_classification.ipynb)).
  - `new_events.json`: Main event list for detection.
  - `new_events_with_ids.json`: Events with unique IDs, useful for triple files creation and later generation of the KG.

- [`filtered_news/`](filtered_news/)
  - `filtered_news_with_keywords_v2.csv`: Default news input. It contains the final filtered set.
  - Other CSVs for alternative news datasets.

- [`output_detection/`](output_detection/)
  - Experiment results in json format.

---

## Notebooks

Additional analysis and utility notebooks:
- [`EDA-DATASET.ipynb`](EDA-DATASET.ipynb): Exploratory data analysis and initial clean up of the [`FNSPID`](https://github.com/Zdong104/FNSPID_Financial_News_Dataset) news dataset.
- [`event_classification.ipynb`](event_classification.ipynb): Event preprocessing (adding categories and geograpicla locations).
- [`event_detection_analysis.ipynb`](event_detection_analysis.ipynb): Analysis of the event detection results. In this notebook we also generate the necessary triples and files for the knowledge graph generation.
- [`fast_fuzzy_search.ipynb`](fast_fuzzy_search.ipynb): Additional filtering of the news set using fuzzy matching, we only keep he news that contain vocabulary and terms related to the events from the list.


---