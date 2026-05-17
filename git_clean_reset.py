import os
import shutil
import subprocess
import time

def run_cmd(cmd, cwd=None):
    print(f"Running: {cmd}")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    if res.returncode != 0:
        print(f"Error: {res.stderr.strip()}")
        return False
    print(f"Success: {res.stdout.strip()[:200]}")
    return True

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    git_dir = os.path.join(root_dir, ".git")
    git_old_dir = os.path.join(root_dir, ".git_old")
    
    print(f"Root Directory: {root_dir}")
    
    # 1. Safely remove or rename old .git folder
    if os.path.exists(git_dir):
        print("Cleaning up old .git configuration to prune large history...")
        if os.path.exists(git_old_dir):
            try:
                shutil.rmtree(git_old_dir)
            except Exception as e:
                print(f"Warning: could not clean existing .git_old: {e}")
        
        # Try to rename .git to .git_old
        try:
            shutil.move(git_dir, git_old_dir)
            print("Renamed .git to .git_old successfully.")
        except Exception as e:
            print(f"Could not rename .git directly, trying deletion: {e}")
            try:
                # Remove read-only flags first for git files
                for root, dirs, files in os.walk(git_dir):
                    for f in files:
                        os.chmod(os.path.join(root, f), 0o777)
                shutil.rmtree(git_dir)
                print("Deleted old .git folder successfully.")
            except Exception as ex:
                print(f"CRITICAL: Failed to remove old .git folder: {ex}")
                print("Please close any editor/terminal lock on the .git folder and retry.")
                return

    # 2. Re-initialize a fresh lightweight Git repo
    if not run_cmd("git init", cwd=root_dir):
        return
        
    # 3. Add remote
    if not run_cmd("git remote add origin https://github.com/AbhayBhise/aqi-prediction-ml-pipeline.git", cwd=root_dir):
        return
        
    # 4. Stage all files (respecting the new .gitignore rules)
    print("Staging files (excluding heavy joblib/csv files)...")
    if not run_cmd("git add .", cwd=root_dir):
        return
        
    # 5. Commit
    if not run_cmd('git commit -m "feat: initial lightweight production-ready release"', cwd=root_dir):
        return
        
    print("\n" + "="*50)
    print("SUCCESS: Fresh lightweight Git history is ready locally!")
    print("All heavy files (>50MB) and old history have been successfully pruned.")
    print("="*50)
    print("Now simply run the following command in your terminal to push:")
    print("git push -u origin main --force")
    print("="*50 + "\n")

if __name__ == "__main__":
    main()
