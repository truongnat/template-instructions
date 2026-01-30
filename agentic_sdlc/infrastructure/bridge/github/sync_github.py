import os
import re
from github import Github
from dotenv import load_dotenv
from agentic_sdlc.intelligence.reasoning.knowledge_graph.graph_brain import LocalKnowledgeGraph

load_dotenv()


class GitHubGraphBridge:
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        self.repo_name = os.getenv("GITHUB_REPO")
        
        if not self.token or not self.repo_name:
            print("⚠️ Missing GITHUB_TOKEN or GITHUB_REPO. Skipping GitHub sync.")
            self.valid = False
            return
        self.kg = LocalKnowledgeGraph()
        self.github = Github(self.token)
        self.repo = self.github.get_repo(self.repo_name)
        self.valid = True

    def close(self):
        if self.valid:
            self.kg.close()

    def sync_issues(self):
        if not self.valid: return
        print(f"Syncing issues from {self.repo_name}...")
        issues = self.repo.get_issues(state='all')
        
        for issue in issues:
            print(f"Processing Issue #{issue.number}: {issue.title}")
            
            # 1. Create/Update Issue Node
            issue_id = f"ISSUE-{issue.number}"
            self.kg.upsert_node(issue_id, "Issue", {
                "number": issue.number,
                "title": issue.title,
                "state": issue.state,
                "url": issue.html_url
            })

            # 2. Link Labels
            for label in issue.labels:
                label_id = f"LABEL-{label.name.upper()}"
                self.kg.upsert_node(label_id, "Label", {"name": label.name, "color": label.color})
                self.kg.create_relationship(issue_id, label_id, "HAS_LABEL")

            # 3. Link to Files mentioned in body
            if issue.body:
                paths = re.findall(r'[\w\-\.\/]+\.(?:py|js|ts|md|yml|json|md)', issue.body)
                for path in set(paths):
                    clean_path = path.strip('`()[]')
                    # Search for existing file nodes
                    files = self.kg.find_nodes(label="File", query=clean_path)
                    for f in files:
                        self.kg.create_relationship(issue_id, f['id'], "RELATES_TO_FILE")

        print("[SUCCESS] GitHub Issues synced to Local Graph.")

if __name__ == "__main__":
    bridge = GitHubGraphBridge()
    try:
        bridge.sync_issues()
    finally:
        bridge.close()
