import argparse
import sys
from pathlib import Path
from . import skill_utils

def list_skills(args):
    """List all installed skills."""
    skills = skill_utils.find_all_skills()
    if not skills:
        print("📭 No skills found.")
        return
        
    print(f"📋 Installed Skills ({len(skills)}):")
    print("-" * 50)
    for skill in sorted(skills, key=lambda s: (s.location != 'project', s.name)):
        loc = f"({skill.location})"
        print(f"{skill.name:20} {loc:10} {skill.description[:60]}...")

def read_skills(args):
    """Read specific skills to stdout."""
    if not args.names:
        print("❌ Error: At least one skill name is required.")
        return
        
    # Split comma separated names if any
    names = []
    for n in args.names:
        names.extend([x.strip() for x in n.split(',')])
        
    for name in names:
        skill = skill_utils.find_skill(name)
        if not skill:
            print(f"❌ Skill not found: {name}", file=sys.stderr)
            continue
            
        print(f"--- SKILL: {skill.name} ---")
        print(f"Base Directory: {skill.path}")
        print("-" * 20)
        print(skill.content)
        print("-" * 20)
        print()

def sync_skills(args):
    """Sync skills to AGENTS.md."""
    skills = skill_utils.find_all_skills()
    if not skills:
        print("⚠️ No skills to sync. Install skills first.")
        return
        
    output = args.output or "AGENTS.md"
    skill_utils.update_agents_md(skills, output)
    print(f"✅ Synced {len(skills)} skills to {output}")

def main(args=None):
    if args is None:
        args = sys.argv[1:]
        
    parser = argparse.ArgumentParser(prog="asdlc skills", description="Skills management (OpenSkills compatible)")
    subparsers = parser.add_subparsers(dest="command", help="Skills commands")
    
    # List
    subparsers.add_parser("list", help="List all installed skills")
    
    # Read
    read_parser = subparsers.add_parser("read", help="Read skill(s) (for AI agents)")
    read_parser.add_argument("names", nargs="+", help="Skill names (comma separated also supported)")
    
    # Sync
    sync_parser = subparsers.add_parser("sync", help="Update AGENTS.md with installed skills")
    sync_parser.add_argument("-o", "--output", help="Output file (default: AGENTS.md)")
    
    parsed_args = parser.parse_args(args)
    
    commands = {
        "list": list_skills,
        "read": read_skills,
        "sync": sync_skills
    }
    
    if parsed_args.command in commands:
        commands[parsed_args.command](parsed_args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
