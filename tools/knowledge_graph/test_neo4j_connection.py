#!/usr/bin/env python3
"""
Test Neo4j Connection

Simple script to verify Neo4j Cloud connection works.
"""

import os
import sys
from pathlib import Path

# Fix Windows console encoding - must be done before any print statements
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, OSError):
        pass

# Symbols with ASCII fallback for Windows compatibility
def _get_symbol(unicode_char, ascii_fallback):
    try:
        unicode_char.encode(sys.stdout.encoding or 'utf-8')
        return unicode_char
    except (UnicodeEncodeError, LookupError):
        return ascii_fallback

SYM_OK = _get_symbol('✅', '[OK]')
SYM_ERR = _get_symbol('❌', '[ERR]')
SYM_INFO = _get_symbol('📋', '[INFO]')
SYM_PLUG = _get_symbol('🔌', '[CONN]')
SYM_STATS = _get_symbol('📊', '[STATS]')
SYM_CHART = _get_symbol('📈', '[DATA]')

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from dotenv import load_dotenv
    print(f"{SYM_OK} dotenv imported successfully")
except ImportError:
    print(f"{SYM_ERR} Error: python-dotenv not installed")
    print("   Run: pip install python-dotenv")
    sys.exit(1)

try:
    from neo4j import GraphDatabase
    print(f"{SYM_OK} neo4j driver imported successfully")
except ImportError:
    print(f"{SYM_ERR} Error: neo4j driver not installed")
    print("   Run: pip install neo4j")
    sys.exit(1)

# Load environment variables
load_dotenv()
print(f"{SYM_OK} Environment variables loaded")

# Get credentials
uri = os.getenv('NEO4J_URI')
username = os.getenv('NEO4J_USERNAME')
password = os.getenv('NEO4J_PASSWORD')
database = os.getenv('NEO4J_DATABASE', 'neo4j')

print(f"\n{SYM_INFO} Connection Details:")
print(f"   URI: {uri}")
print(f"   Username: {username}")
print(f"   Password: {'*' * len(password) if password else 'NOT SET'}")
print(f"   Database: {database}")

if not all([uri, username, password]):
    print(f"\n{SYM_ERR} Error: Missing Neo4j credentials in .env file")
    print("   Required: NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD")
    sys.exit(1)

print(f"\n{SYM_PLUG} Attempting to connect to Neo4j Cloud...")

try:
    # Create driver
    driver = GraphDatabase.driver(
        uri,
        auth=(username, password)
    )
    print(f"{SYM_OK} Driver created successfully")
    
    # Verify connectivity
    driver.verify_connectivity()
    print(f"{SYM_OK} Connection verified!")
    
    # Test query
    with driver.session(database=database) as session:
        result = session.run("RETURN 'Hello Neo4j!' AS message")
        record = result.single()
        print(f"{SYM_OK} Test query successful: {record['message']}")
        
        # Get database info
        result = session.run("""
            CALL dbms.components() 
            YIELD name, versions, edition 
            RETURN name, versions[0] as version, edition
        """)
        for record in result:
            print(f"\n{SYM_STATS} Database Info:")
            print(f"   Name: {record['name']}")
            print(f"   Version: {record['version']}")
            print(f"   Edition: {record['edition']}")
        
        # Count existing nodes
        result = session.run("MATCH (n) RETURN count(n) as nodeCount")
        count = result.single()['nodeCount']
        print(f"\n{SYM_CHART} Current node count: {count}")
    
    driver.close()
    print(f"\n{SYM_OK} All tests passed! Neo4j connection is working.")
    
except Exception as e:
    print(f"\n{SYM_ERR} Connection failed: {e}")
    print("\nTroubleshooting:")
    print("1. Check your .env file has correct credentials")
    print("2. Verify your Neo4j AuraDB instance is running")
    print("3. Check your internet connection")
    print("4. Ensure firewall allows connection to Neo4j Cloud")
    sys.exit(1)

