import csv, pathlib, shutil
from neo4j import GraphDatabase, basic_auth
import json

# --- SETTINGS --------------------------------------------------
NEO4J_URI      = "bolt://localhost:7687"   # default for Desktop
NEO4J_USER     = "neo4j"
NEO4J_PASSWORD = "finkg v2"             # DB password
COPY_TO_IMPORT = True                      # False -> leave file where it is
TRIPLES_FOLDER = "csvTriples"
DATABASE = "finkg"
# ---------------------------------------------------------------------


def load_2_neo(csv_path: pathlib.Path, driver):
    csv_path = csv_path.expanduser().resolve()

    if COPY_TO_IMPORT:
        neo_home = pathlib.Path.home() / ".Neo4jDesktop" / "relate-data"
        import_dirs = list(neo_home.glob("*/db/*/import"))
        if import_dirs:
            dest = import_dirs[0] / csv_path.name
            shutil.copy2(csv_path, dest)
            print(f"Copied CSV to {dest}")

    with driver.session() as session, csv_path.open(newline='', encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)                 
        subj_label, _, obj_label = header     
        print(f"Using labels: subject: {subj_label}, object: {obj_label}")

        for subj, rel, obj in reader:         
            cypher = (
                f"MERGE (s:`{subj_label}` {{id:$subj}}) "
                f"MERGE (o:`{obj_label}` {{id:$obj}}) "
                f"MERGE (s)-[:`{rel}`]->(o)"
            )

            session.run(cypher, subj=subj, obj=obj)

    print(f"Finished importing {csv_path.name}")

def add_event_types():
    # get the saved list of events, which contains all the events with ids and types
    with open("new_events_with_ids.json") as f:
        content = json.load(f)
        id_event_type_map = {ev["event_id"]:ev["event_type"] for ev in content}

    # list of events
    with open("csvTriples/IMPACTS.csv") as f:
        # get the list of events
        events = set(line.split(",")[0].strip() for line in f.readlines()[1:])  # skip header
        for event in events:

            event_types = id_event_type_map.get(event) # an event has many different types

            event_types=[cats.split(".")[1] for cats in event_types]
            # print(event_types)
            
            for event_type in event_types:
                with driver.session() as session:
                    cypher = (
                        f"MERGE (s:Event {{id:$event}}) "
                        f"MERGE (o:Event_Type {{id:$type}}) "
                        f"MERGE (s)-[:`EVENT_HAS_TYPE`]->(o)"
                    )
                    session.run(cypher, event=event, type=event_type)
                    # print(f"Added triple {event}, has type, {event_type}")
    print("Added Event type triples.")


def remove_event_nodes():
    with driver.session() as session:
        cypher = """
        MATCH (n:Event)
        DETACH DELETE n;
        """
        session.run(cypher)

        cypher = """
        MATCH (n:Event_Type)
        DETACH DELETE n;
        """
        session.run(cypher)

    print("Deleted event and event type nodes.")


    
if __name__ == "__main__":

    driver = GraphDatabase.driver(NEO4J_URI,
                                  database=DATABASE,
                                  auth=basic_auth(NEO4J_USER, NEO4J_PASSWORD))

    remove_event_nodes()
    add_event_types()

    file = "IMPACTS.csv"
    load_2_neo(pathlib.Path(f"{TRIPLES_FOLDER}/{file}"), driver)

    driver.close()
