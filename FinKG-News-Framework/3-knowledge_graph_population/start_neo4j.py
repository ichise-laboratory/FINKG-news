import csv, pathlib, shutil, sys, os, json
from neo4j import GraphDatabase, basic_auth
from dotenv import load_dotenv

load_dotenv("../../.env")

# --- SETTINGS --------------------------------------------------
NEO4J_URI      = os.environ.get("NEO_URL", "bolt://localhost:7687")
NEO4J_USER     = os.environ.get("NEO_USERNAME", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO_PASSWORD")
COPY_TO_IMPORT = True
TRIPLES_FOLDER = "csvTriples"
DATABASE       = os.environ.get("NEO_DATABASE", "finkg")
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

            if subj in sp_companies:
                cypher += "SET s:SP "
            if obj in sp_companies:
                cypher += "SET o:SP "

            session.run(cypher, subj=subj, obj=obj)

    print(f"Finished importing {csv_path.name}")

def clean_nodes(driver):
    with driver.session() as session:
        cypher = (f"MATCH (n) DETACH DELETE n")
        session.run(cypher)
        
    print("Deleted all nodes.")

def add_major_industry_triples(driver):
    ## SIC CODE
    # made up of 4 digits
    # the first two digits represent the major industry group
    # create triples of the form Industry, INDUSTRY_BELONGS_TO_MAJOR_GROUP, Major_Industry_Group
    with open("csvTriples/BELONGS_TO_INDUSTRY_OF.csv") as f:
        # get the list of industries
        industries = set(line.split(",")[-1].strip() for line in f.readlines()[1:])  # skip header
        for sic_code in industries:
            major_group = sic_code[:2] # get first 2 digits
            # create the triple
            with driver.session() as session:
                cypher = (
                    f"MERGE (s:Industry {{id:$sic_code}}) "
                    f"MERGE (o:Major_industry_group {{id:$major_group}}) "
                    f"MERGE (s)-[:`INDUSTRY_BELONGS_TO_MAJOR_GROUP`]->(o)"
                )
                session.run(cypher, sic_code=sic_code, major_group=major_group)
    print("Added major industry triples.")

def add_event_types(driver):
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
    print("Added Event type triples.")

if __name__ == "__main__":

    with open("csvTriples/BELONGS_TO_INDUSTRY_OF.csv") as f:
        sp_companies = set(line.split(",")[0].strip() for line in f.readlines()[1:])  # skip header
        print(f"Loaded {len(sp_companies)} SP companies.")
        print(f"Example: {list(sp_companies)[:5]}")

    driver = GraphDatabase.driver(NEO4J_URI,
                                  database=DATABASE,
                                  auth=basic_auth(NEO4J_USER, NEO4J_PASSWORD))
    
    # first remove all the nodes
    clean_nodes(driver)

    # add major industry group
    add_major_industry_triples(driver)
    # and event types
    add_event_types(driver)

    # add the rest of the triples
    for file in os.listdir(TRIPLES_FOLDER):
        load_2_neo(pathlib.Path(f"{TRIPLES_FOLDER}/{file}"), driver)

    driver.close()
