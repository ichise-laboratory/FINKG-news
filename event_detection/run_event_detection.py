import ollama
import json
import pandas as pd
import time
from datetime import datetime

### SETTINGS

news_csv = "filtered_news/filtered_news_with_keywords_v2.csv" # path with news to process
events_path = "event_jsons/new_events.json" # path with the list of events to spot in the news

# save experiment as
timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
experiment_name = f"output_detection/experiment_{timestamp}.jsonl"

DEBUG = True

event_chunk_size = 20 # how many events to fit inside the system prompt
token_limit = 2600 # token limit for the model, we will truncate the news if it exceeds this limit, otherwise some models will ignore the main task from the system prompt

llm_model = "llama3:70b"  # model to use, make sure you have it downloaded in ollama


## Event processing
with open(events_path,mode="r") as f:
    events_json = json.load(f)

events = []

# the events are grouped by year
# use the year to give each event a unique id

for year in events_json:
    for i,event in enumerate(events_json[year]):
        events.append(
            {
                "event_id":f"{year}_{i}",
                "event_text":event["text"],
                "event_date":event["date"],
            }
        )

# read and format the events
def format_events(events):
    formatted_events = ""
    for event in events:
        formatted_events += "\n"
        for k,v in event.items():
            formatted_events += f"{k}: {v}\n"
    return formatted_events

# many models cannot handle a large system prompt, so we have to chunk the event list into x groupd of y news
def get_event_chunks(news_year, event_chunk_size=20):
    events_filtered = [event for event in events if int(event["event_id"].split("_")[0]) <= int(news_year)]
    #chunking
    chunk_size = 20
    event_list_chunks = [
        events_filtered[i:i + event_chunk_size]
        for i in range(0, len(events_filtered), chunk_size)
    ]
    return event_list_chunks


### PROMPTS
def get_system_prompt(events):
    return f"""This is a list of events that took part in the 21st century:
                {format_events(events)}
            
            You will receive a news article. Your task is to detect in said article the top 5 events from the previous list with confidence scores that range from 0 to 1. 
            
            Output format:
            [{{
                "event_id":"2023_27"
                "event":"Somalia admitted to East African Community.",
                "confidence":0.9}},
                {{
                "event_id":"2023_12"
                "event_text":"2023 Ecuadorian political crisis.",
                "confidence":0.4}},
                <keep adding until 5 events in the list>]
                
            Do not inlcude additional text, just the list of events in the specified format.
            Never include events that do not apear in the list I provided.
            If you are sure none of the events in the list match the news, output an empty list. 
            However, at least try to include the most related events, with high confidence (0.8 or above) if you are sure it is explicit in the news and low confidence if you are unsure. """

def get_user_prompt(news_row):

    return f"""
    Date:{news_row["Date"]}
    Title:{news_row["Article_title"]}
    Text:{news_row["Article"]}""" # return the date title and the text


### MAIN CODE

# temporal
# use this if you need to resume the experiment from a specific news id
start_processing_flag = False
# checkpoint_index = 14771
# checkpoint_index = 22275
checkpoint_index = 155920

# START PROCESSING
for news in pd.read_csv(news_csv, chunksize=1):

    # temporal
    # use this if you need to resume the experiment from a specific news id
    if not start_processing_flag:
        if news["og_index"].iloc[0] == checkpoint_index:
            start_processing_flag = True
            print("Found the checkpoint news\n",news["Article"])
        else:
            continue # skip news and go to the next row
        
    user_message = get_user_prompt(news.iloc[0])

    if DEBUG:
        print("\nProcessing news:")
        print("User:",user_message)

    # to avoid unnecessary checking and reduce computing time, we just check the events from the same year and before, as future events cannot influence past news
    news_year = news.iloc[0]["Date"].split("-")[0]
    event_list_chunks = get_event_chunks(news_year,event_chunk_size)

    for events_chunk in event_list_chunks:        

        system_prompt = get_system_prompt(events_chunk)

        # check token length
        if DEBUG:
            total_tokens = len(user_message.split()) + len(system_prompt.split())
            print(f"news text tokens: {len(user_message.split())}")
            print(f"system prompt tokens: {len(system_prompt.split())}")
            print(f"total: {total_tokens}")
        
        if total_tokens > token_limit: # limit is around 2600 tokens for this model for input
            desired_user_tokens = token_limit - len(system_prompt.split())
            user_message = ' '.join(user_message.split()[:desired_user_tokens])  # truncate user message to fit token limit


        time_init = time.time()
        response = ollama.chat(
                model=llm_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]
            )

        time_end = time.time()

        model_output = response['message']['content']
        
        if DEBUG:
            print("Total Inference time:",time_end - time_init)
            # print("System:",system_prompt)
            print("Model response:",model_output)

        # save the results
        result = {
            "news_id": news.index[0],
            "user_prompt": user_message,
            "system_prompt": system_prompt,
            "response": model_output,
            "total_tokens": len(user_message.split()) + len(system_prompt.split()),
            "inference_time": round(time.time() - time_init, 2)
        }

        with open(experiment_name, "a", encoding="utf-8") as f:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")