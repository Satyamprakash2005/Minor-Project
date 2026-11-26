"""
push_to_github.py
Push the repository directly to GitHub using Python without needing git.exe.
"""

import sys
import getpass
from dulwich.repo import Repo
from dulwich.porcelain import push

REPO_PATH = r"c:\Users\ASUS\Desktop\minor project"

def main():
    print("=" * 60)
    print("  Push Minor Project to GitHub")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        token = sys.argv[1].strip()
    else:
        token = input("Paste your GitHub Personal Access Token: ").strip()
    
    if not token:
        print("[ERROR] Token cannot be empty.")
        sys.exit(1)

    remote_url = f"https://{token}@github.com/Satyamprakash2005/Minor-Project.git"
    
    try:
        repo = Repo(REPO_PATH)
        print("\n[INFO] Connected to local repository.")
        print("[INFO] Pushing master branch to origin/main...")
        push(repo, remote_url, refspecs=[b"refs/heads/master:refs/heads/main"])
        print("\n[SUCCESS] Successfully pushed all files to:")
        print("          https://github.com/Satyamprakash2005/Minor-Project")
    except Exception as e:
        print(f"\n[ERROR] Failed to push: {e}")
        print("\nNote: Make sure your GitHub token has 'Contents: Read and write' permissions.")

if __name__ == "__main__":
    main()
