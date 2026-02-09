
import shutil
import os
import sys

def copy_project():
    src_dir = os.getcwd()
    build_root = "/tmp/agentic_build"
    dist_root = "/tmp/agentic_dist"
    
    if os.path.exists(build_root):
        shutil.rmtree(build_root)
    if os.path.exists(dist_root):
        shutil.rmtree(dist_root)
        
    os.makedirs(build_root)
    os.makedirs(dist_root)
    
    # Items to copy
    to_copy = ["pyproject.toml", "README.md", "LICENSE", "MANIFEST.in"]
    for item in to_copy:
        try:
            shutil.copy2(item, build_root)
        except Exception as e:
            print(f"Error copying {item}: {e}")

    # Copy package dir
    def ignore_patterns(path, names):
        ignore_list = []
        for name in names:
            if name in ['lib', '__pycache__', '.DS_Store'] or name.endswith('.pyc') or name.endswith('.egg-info'):
                ignore_list.append(name)
        return ignore_list

    src_pkg = os.path.join(src_dir, "agentic_sdlc")
    dst_pkg = os.path.join(build_root, "agentic_sdlc")
    
    try:
        shutil.copytree(src_pkg, dst_pkg, ignore=ignore_patterns, dirs_exist_ok=True)
        print(f"Copied package to {dst_pkg}")
    except Exception as e:
        print(f"Error copying package: {e}")

    # Check size
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(build_root):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                try:
                    total_size += os.path.getsize(fp)
                except: pass
    
    print(f"Total build size: {total_size} bytes")
    if total_size < 100000:
        print("WARNING: Build size is too small!")
        sys.exit(1)

if __name__ == "__main__":
    copy_project()
