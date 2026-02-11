
import subprocess
import os
import shutil
from pathlib import Path

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

def test_git_worktree_feature():
    print("🧪 Testing Git Worktree (Worktrunk foundation)...")
    
    # 1. Create a temporary branch
    branch_name = "test-worktree-branch"
    run_cmd(f"git branch -D {branch_name}") # Clean up if exists
    rc, out, err = run_cmd(f"git branch {branch_name}") # Create BUT DON'T CHECKOUT
    if rc != 0:
        print(f"❌ Failed to create branch: {err}")
        return
    
    # 2. Add a worktree
    worktree_path = os.path.abspath("tests/temp_worktree_test")
    if os.path.exists(worktree_path):
        shutil.rmtree(worktree_path)
        run_cmd(f"git worktree prune")
        
    print(f"adding worktree at {worktree_path}...")
    rc, out, err = run_cmd(f"git worktree add {worktree_path} {branch_name}")
    
    if rc == 0:
        print("✅ Git worktree ADD successful")
    else:
        print(f"❌ Git worktree ADD failed: {err}")
        run_cmd("git checkout main")
        run_cmd(f"git branch -D {branch_name}")
        return

    # 3. Verify worktree exists
    rc, out, err = run_cmd("git worktree list")
    if worktree_path in out:
        print("✅ Worktree correctly listed")
    else:
        print(f"❌ Worktree NOT in list: {out}")

    # 4. Clean up
    print("Cleaning up...")
    run_cmd(f"git worktree remove {worktree_path}")
    run_cmd("git checkout main")
    run_cmd(f"git branch -D {branch_name}")
    
    # Prune just in case
    run_cmd("git worktree prune")
    
    if not os.path.exists(worktree_path):
        print("✅ Cleanup successful")
    else:
        print("⚠️ Warning: Worktree directory still exists")

    print("\n🎉 Git Worktree Feature Test COMPLETE!")

if __name__ == "__main__":
    test_git_worktree_feature()
