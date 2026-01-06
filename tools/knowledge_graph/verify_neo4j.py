import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

def verify_data():
    driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))
    with driver.session() as session:
        result = session.run("MATCH (f:File) RETURN f.path as path, f.summary as summary")
        records = list(result)
        if records:
            print(f"[SUCCESS] Found {len(records)} files in Neo4j:")
            for record in records:
                print(f" - {record['path']}: {record['summary']}")
        else:
            print("[WARNING] No files found in Neo4j.")
    driver.close()

if __name__ == "__main__":
    verify_data()
