import os
import re
from github import Github
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

# Config
URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")

class GitHubNeo4jBridge:
    def __init__(self):
        if not all([URI, USERNAME, PASSWORD, GITHUB_TOKEN, GITHUB_REPO]):
            raise Exception("Missing environment variables in .env")
        self.driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))
        self.github = Github(GITHUB_TOKEN)
        self.repo = self.github.get_repo(GITHUB_REPO)

    def close(self):
        self.driver.close()

    def sync_issues(self):
        print(f"Syncing issues from {GITHUB_REPO}...")
        issues = self.repo.get_issues(state='all')
        
        with self.driver.session() as session:
            for issue in issues:
                print(f"Processing Issue #{issue.number}: {issue.title}")
                
                # 1. Create/Update Issue Node
                session.run("""
                    MERGE (i:Issue {number: $number})
                    SET i.title = $title, i.state = $state, i.url = $url, i.body = $body
                """, number=issue.number, title=issue.title, state=issue.state, url=issue.html_url, body=issue.body)

                # 2. Extract Labels
                for label in issue.labels:
                    session.run("""
                        MATCH (i:Issue {number: $number})
                        MERGE (l:Label {name: $label_name})
                        SET l.color = $color
                        MERGE (i)-[:HAS_LABEL]->(l)
                    """, number=issue.number, label_name=label.name, color=label.color)

                # 3. Simple Heuristic: Link to Files mentioned in body
                if issue.body:
                    # Look for paths like d:\dev\... or just relative paths mentioned
                    # This regex looks for common file extensions in the body
                    paths = re.findall(r'[\w\-\.\/]+\.(?:py|js|ts|md|yml|json|md)', issue.body)
                    for path in set(paths):
                        # Clean up path from some markdown characters
                        clean_path = path.strip('`()[]')
                        
                        # Try to match existing File nodes in Neo4j
                        session.run("""
                            MATCH (i:Issue {number: $number})
                            MATCH (f:File)
                            WHERE f.path ENDS WITH $path OR $path ENDS WITH f.path
                            MERGE (i)-[:RELATES_TO_FILE]->(f)
                        """, number=issue.number, path=clean_path)

        print("[SUCCESS] GitHub Issues synced to Neo4j Cloud.")

if __name__ == "__main__":
    try:
        bridge = GitHubNeo4jBridge()
        bridge.sync_issues()
        bridge.close()
    except Exception as e:
        print(f"[ERROR] {e}")
