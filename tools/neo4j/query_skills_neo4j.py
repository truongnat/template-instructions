#!/usr/bin/env python3
"""
Query Skills from Neo4j Knowledge Graph

This script provides various queries to explore skills, technologies,
and relationships in the Neo4j knowledge graph.

Usage:
    python bin/query_skills_neo4j.py --all-skills
    python bin/query_skills_neo4j.py --tech "Neo4j"
    python bin/query_skills_neo4j.py --skill "User Research"
    python bin/query_skills_neo4j.py --learning-path "UI/UX Design"
"""

import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
import argparse
from typing import List, Dict

load_dotenv()


class Neo4jSkillQuery:
    """Query skills from Neo4j knowledge graph"""
    
    def __init__(self, uri: str, user: str, password: str, database: str = "neo4j"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database
    
    def close(self):
        self.driver.close()
    
    def get_all_skills(self) -> List[Dict]:
        """Get all skills in the knowledge base"""
        with self.driver.session(database=self.database) as session:
            result = session.run("""
                MATCH (s:Skill)<-[:TEACHES]-(k:KBEntry)
                RETURN s.name as skill, 
                       s.level as level,
                       count(k) as kb_count,
                       collect(k.title) as kb_entries
                ORDER BY kb_count DESC, skill
            """)
            return [dict(record) for record in result]
    
    def get_skills_by_technology(self, tech: str) -> List[Dict]:
        """Get skills related to a specific technology"""
        with self.driver.session(database=self.database) as session:
            result = session.run("""
                MATCH (t:Technology {name: $tech})<-[:USES_TECHNOLOGY]-(k:KBEntry)-[:TEACHES]->(s:Skill)
                RETURN s.name as skill,
                       s.level as level,
                       k.title as kb_entry
                ORDER BY skill
            """, tech=tech)
            return [dict(record) for record in result]
    
    def get_related_skills(self, skill_name: str) -> List[Dict]:
        """Get skills related to a specific skill"""
        with self.driver.session(database=self.database) as session:
            result = session.run("""
                MATCH (s1:Skill {name: $skill})-[r:RELATED_TO]-(s2:Skill)
                RETURN s2.name as related_skill,
                       r.strength as strength
                ORDER BY strength DESC
                LIMIT 10
            """, skill=skill_name)
            return [dict(record) for record in result]
    
    def get_learning_path(self, category: str) -> List[Dict]:
        """Get learning path for a category"""
        with self.driver.session(database=self.database) as session:
            result = session.run("""
                MATCH (c:Category {name: $category})<-[:BELONGS_TO]-(k:KBEntry)-[:TEACHES]->(s:Skill)
                RETURN k.title as kb_entry,
                       k.date as date,
                       collect(s.name) as skills
                ORDER BY date
            """, category=category)
            return [dict(record) for record in result]
    
    def get_technologies(self) -> List[Dict]:
        """Get all technologies and their usage count"""
        with self.driver.session(database=self.database) as session:
            result = session.run("""
                MATCH (t:Technology)<-[:USES_TECHNOLOGY]-(k:KBEntry)
                RETURN t.name as technology,
                       count(k) as kb_count
                ORDER BY kb_count DESC, technology
            """)
            return [dict(record) for record in result]
    
    def get_skill_prerequisites(self, skill_name: str) -> List[Dict]:
        """Get prerequisite skills for a given skill"""
        with self.driver.session(database=self.database) as session:
            result = session.run("""
                MATCH (s1:Skill {name: $skill})<-[:TEACHES]-(k:KBEntry)-[:TEACHES]->(s2:Skill)
                WHERE s1 <> s2 AND s2.level = 'beginner'
                RETURN DISTINCT s2.name as prerequisite,
                       s2.level as level
                ORDER BY prerequisite
            """, skill=skill_name)
            return [dict(record) for record in result]
    
    def search_skills(self, query: str) -> List[Dict]:
        """Search skills by keyword"""
        with self.driver.session(database=self.database) as session:
            result = session.run("""
                MATCH (s:Skill)<-[:TEACHES]-(k:KBEntry)
                WHERE toLower(s.name) CONTAINS toLower($query)
                   OR toLower(k.title) CONTAINS toLower($query)
                RETURN DISTINCT s.name as skill,
                       s.level as level,
                       collect(k.title) as kb_entries
                ORDER BY skill
            """, query=query)
            return [dict(record) for record in result]
    
    def get_author_expertise(self, author: str) -> List[Dict]:
        """Get skills by author"""
        with self.driver.session(database=self.database) as session:
            result = session.run("""
                MATCH (p:Person {name: $author})-[:CREATED]->(k:KBEntry)-[:TEACHES]->(s:Skill)
                RETURN k.title as kb_entry,
                       collect(s.name) as skills,
                       k.date as date
                ORDER BY date DESC
            """, author=author)
            return [dict(record) for record in result]


def print_skills(skills: List[Dict], title: str):
    """Pretty print skills"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")
    
    if not skills:
        print("  No results found.")
        return
    
    for i, skill in enumerate(skills, 1):
        print(f"{i}. {skill}")


def main():
    parser = argparse.ArgumentParser(description='Query Skills from Neo4j')
    parser.add_argument('--all-skills', action='store_true', help='List all skills')
    parser.add_argument('--tech', type=str, help='Skills for specific technology')
    parser.add_argument('--skill', type=str, help='Related skills for a skill')
    parser.add_argument('--learning-path', type=str, help='Learning path for category')
    parser.add_argument('--technologies', action='store_true', help='List all technologies')
    parser.add_argument('--search', type=str, help='Search skills by keyword')
    parser.add_argument('--author', type=str, help='Skills by author (e.g., @UIUX)')
    parser.add_argument('--prerequisites', type=str, help='Prerequisites for a skill')
    args = parser.parse_args()
    
    # Get credentials
    uri = os.getenv('NEO4J_URI')
    username = os.getenv('NEO4J_USERNAME')
    password = os.getenv('NEO4J_PASSWORD')
    database = os.getenv('NEO4J_DATABASE', 'neo4j')
    
    if not all([uri, username, password]):
        print("❌ Error: Neo4j credentials not found in .env file")
        return
    
    query = Neo4jSkillQuery(uri, username, password, database)
    
    try:
        if args.all_skills:
            skills = query.get_all_skills()
            print_skills(skills, "All Skills in Knowledge Base")
        
        elif args.tech:
            skills = query.get_skills_by_technology(args.tech)
            print_skills(skills, f"Skills for {args.tech}")
        
        elif args.skill:
            skills = query.get_related_skills(args.skill)
            print_skills(skills, f"Skills Related to '{args.skill}'")
        
        elif args.learning_path:
            path = query.get_learning_path(args.learning_path)
            print_skills(path, f"Learning Path: {args.learning_path}")
        
        elif args.technologies:
            techs = query.get_technologies()
            print_skills(techs, "All Technologies")
        
        elif args.search:
            skills = query.search_skills(args.search)
            print_skills(skills, f"Search Results for '{args.search}'")
        
        elif args.author:
            expertise = query.get_author_expertise(args.author)
            print_skills(expertise, f"Expertise by {args.author}")
        
        elif args.prerequisites:
            prereqs = query.get_skill_prerequisites(args.prerequisites)
            print_skills(prereqs, f"Prerequisites for '{args.prerequisites}'")
        
        else:
            print("Please specify a query option. Use --help for options.")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        query.close()


if __name__ == "__main__":
    main()
