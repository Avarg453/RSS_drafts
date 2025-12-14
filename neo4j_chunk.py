from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
load_dotenv()
# URI examples: "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"
URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")
AUTH = (USER, PASSWORD)
# add in a bunch of stuff for connecting to the database locally which i guess needs teh service to be started

# can teh service run idefinitely on my computer? how do i ensure it runs regularly?



# with GraphDatabase.driver(URI, auth=AUTH) as driver:
#     driver.verify_connectivity()
#     print("Connection established.")
