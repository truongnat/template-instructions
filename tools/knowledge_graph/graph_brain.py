import os
import glob
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

class Neo4jBrain:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def initialize_schema(self):
        with self.driver.session() as session:
            # Create constraints
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (f:File) REQUIRE f.path IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (r:Requirement) REQUIRE r.id IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (i:Issue) REQUIRE i.number IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (ro:Role) REQUIRE ro.name IS UNIQUE")
            print("[SUCCESS] Neo4j Schema Initialized")

    def ingest_project_structure(self, base_path):
        """Walks the directory and creates File nodes and directory HIERARCHY."""
        with self.driver.session() as session:
            # Ignore some directories
            ignore_dirs = {'.git', 'node_modules', '.agent', '__pycache__'}
            
            for root, dirs, files in os.walk(base_path):
                # Filter ignore dirs
                dirs[:] = [d for d in dirs if d not in ignore_dirs]
                
                rel_root = os.path.relpath(root, base_path)
                if rel_root == ".": rel_root = "root"
                
                for file in files:
                    rel_path = os.path.relpath(os.path.join(root, file), base_path)
                    ext = os.path.splitext(file)[1]
                    
                    session.run("""
                        MERGE (f:File {path: $path})
                        SET f.name = $name, f.extension = $ext, f.last_updated = timestamp()
                        MERGE (d:Directory {path: $dir})
                        MERGE (d)-[:CONTAINS]->(f)
                    """, path=rel_path, name=file, ext=ext, dir=rel_root)
        print(f"[SUCCESS] Ingested project structure from {base_path}")

    def link_issue_to_file(self, issue_number, file_path, rel_type="AFFECTS"):
        with self.driver.session() as session:
            session.run(f"""
                MERGE (i:Issue {{number: $issue_num}})
                MERGE (f:File {{path: $file_path}})
                MERGE (i)-[:{rel_type}]->(f)
            """, issue_num=issue_number, file_path=file_path)

    def get_context_for_file(self, file_path):
        """Retrieves related requirements and issues for a file."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (f:File {path: $path})
                OPTIONAL MATCH (i:Issue)-[r1]->(f)
                OPTIONAL MATCH (req:Requirement)-[r2]->(f)
                RETURN f.path as path, collect(DISTINCT i.number) as issues, collect(DISTINCT req.id) as requirements
            """, path=file_path)
            return result.single()

if __name__ == "__main__":
    if not URI or not PASSWORD:
        print("[ERROR] NEO4J_URI or NEO4J_PASSWORD not found in .env")
    else:
        brain = Neo4jBrain(URI, USERNAME, PASSWORD)
        try:
            brain.initialize_schema()
            # Ingest current directory
            brain.ingest_project_structure(".")
            print("[SUCCESS] Project brain is now updated in the cloud.")
        except Exception as e:
            print(f"[ERROR] Operation failed: {e}")
        finally:
            brain.close()
