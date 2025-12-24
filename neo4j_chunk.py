from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

from pathlib  import Path

load_dotenv()
# URI examples: "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"
URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")
AUTH = (USER, PASSWORD)

# test sample of json files to try adding to neo4j graph database
test_jsons=["jacobinlat-2025-12-9-14-59-31.json",
"kenklippenstein-2025-10-23-17-41-0.json",
"counterpunch-2025-12-12-6-56-10.json",
"boltsmag-2025-11-10-19-9-31.json"]

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()
    print("Connection established.")
    for test_json in test_jsons:
        # Read the JSON content from the file
        with open(Path('json_dump') / test_json, 'r', encoding='utf-8') as file:
            json_content = file.read()

            # quick print to see that everything is imported correctly
            # print(f"content for {test_json}, {json_content}.")

            # create node from each json file with uID as primary key, and all other json keys as properties
            with driver.session() as session:
                session.run(
                    """
                    CREATE (n:Document $props)
                    """,
                    props={"content": json_content}
                )
                print(f"Node created for {test_json}.")