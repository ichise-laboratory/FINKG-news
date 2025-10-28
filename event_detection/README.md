# Event Detection

In this module we process a set of news articles and detect events within them using a LLM. Results are saved for further analysis and knowledge graph generation.

---

## Table of Contents

- [Setup](#setup)
- [Defining the Events](#defining-the-events)
- [News Dataset Processing](#news-dataset-processing)
- [Running the Event Detection](#running-the-event-detection)
- [Result Analysis](#result-analysis)

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

## Defining the Events

The event detection task requires a predefined list of events to identify in the news corpus. Events are extracted from Wikipedia and stored in a json file. These events are then enriched with additional information such as categories and geographical locations.

**Notebook:** [`event_classification.ipynb`](event_classification.ipynb)

The notebook performs event preprocessing:
- Add categories to the events, following the taxonomy available at ["Event_Type_Taxonomy.png"](Event_Type_Taxonomy.png).
- Assign geographical locations.
- Produce the main event list used for detection.

### Event files

All input and output files for event preprocessing are in the `event_jsons/` directory:

| File | Description |
|------|-------------|
| `dict_wiki_timelines5_geo_country_event.json` | Original Wikipedia event set (no preprocessing). Input to `event_classification.ipynb`. |
| `new_events.json` | Main processed event list produced by `event_classification.ipynb`. Used for event detection. |
| `new_events_with_ids.json` | Same events as `new_events.json` but with unique IDs. Required for creating triple files and building the knowledge graph. |

---

## News Dataset Processing

Here we describe how the news dataset is processed and progressively reduced to obtain the final set used for event detection.

---

### Step 1: Initial Filtering and Cleaning

**Notebook:** [`EDA-DATASET.ipynb`](EDA-DATASET.ipynb)

This notebook performs exploratory data analysis (EDA) and preprocessing of the [FNSPID Financial News Dataset](https://github.com/Zdong104/FNSPID_Financial_News_Dataset).

**Processing steps:**
1. Start with the original **FNSPID** dataset (which contains millions of records).
2. Remove entries with missing (`NaN`) values in relevant fields → ~2 million records.
3. Keep only news referring to companies in the **S&P 500, 400, and 600** indexes.
4. Remove duplicate entries → final set of approximately **662,000 distinct news articles**.

---

### Step 2: Event-Related Filtering

**Notebook:** [`fast_fuzzy_search.ipynb`](fast_fuzzy_search.ipynb)

Even after cleaning, 600K+ articles are too many for an LLM-based processing. Moreover, in previous experiments we observed that many of the news articles do not even mention any detectable events at all. To reduce the dataset size while preserving relevant news, we apply **fast fuzzy keyword matching** against a predefined event-related vocabulary.

This filtering reduces the dataset from **~662,000** to **~80,000** articles, which constitutes the final input set for the event detection task.

Due to its size, the complete dataset is not included in the repository.  
A reduced sample can be found in the `filtered_news/` directory for reference.

## Running the Event Detection

### Model Selection

By default, the script uses the `llama3:70b` model.  
To download a model with Ollama, run:
```sh
ollama pull llama3:70b
```
To use a different model, change the `llm_model` variable in [`run_event_detection.py`](run_event_detection.py).

See available models at [https://ollama.com/library](https://ollama.com/library).

---

### Configuration

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
### Run the main script
---

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
  Output files are saved in the [`output_detection`](output_detection/) folder. Here you can find a reduced example of the expected output format.

---

## Result Analysis

**Notebook:** [`event_detection_analysis.ipynb`](event_detection_analysis.ipynb)

This notebook analyzes the results of the event detection and generates the final **triple files** required for knowledge graph construction.

An example of the expected output format is provided in the `output_detection/` folder.

---

### Generated Triple Files

The following outputs were produced and later stored in the `kg_generation/csvTriples/` directory of the main repository:

| File | Description |
|------|--------------|
| `IMPACTS-CORRECT` | Final and validated set of *Event–Impact* triples. Generated after correcting earlier versions. Includes events detected with confidence ≥ 0.9. |
| `IMPACTS-91percThreshold-CORRECT` | Alternative version of *Event–Impact* triples using a stricter confidence threshold (> 0.9). Contains fewer events but higher precision. |
| `MENTIONS-COMPANY` | Triples linking each *News* item to the *Company* it mentions. |
| `MENTIONS-EVENT` | Triples linking each *News* item to the *Event* it mentions. |

These triples form the basis of the knowledge graph and allow linking detected events to their source news articles and related companies.
