Repository security notes and remediation steps

This project contains a secret (Google Cloud service account JSON) that was detected by GitHub Push Protection and blocked when pushing to GitHub.

Do NOT attempt to re-commit that JSON file. Follow the steps below to remove the secret from git history, add safe ignores, rotate the credential, and push a cleaned repo.

1) Immediately rotate/revoke the exposed credential
- Go to the Google Cloud Console -> IAM & Admin -> Service Accounts.
- Find and revoke/delete the exposed key. Create a new key if needed.

2) Add ignore entry and remove tracked copy from working tree
From your local repo root (PowerShell):
 git rm --cached --ignore-unmatch serviceAccountKey.json
 git add .gitignore
 git commit -m "chore: ignore service account keys and remove tracked copy"

3) Remove the file from repository history (recommended: git-filter-repo)

Recommended (fast & safe): install git-filter-repo and run locally.
 python -m pip install --user git-filter-repo
 git clone --mirror https://github.com/HACKWAVE2025/B58.git repo-mirror.git
 cd repo-mirror.git
 git filter-repo --invert-paths --paths serviceAccountKey.json
 git push --force --tags origin 'refs/heads/*'

Fallback (if git-filter-repo is not available): git filter-branch (deprecated, slower)
 git filter-branch --force --index-filter "git rm --cached --ignore-unmatch serviceAccountKey.json" --prune-empty --tag-name-filter cat -- --all
 rm -r .git/refs/original/; git reflog expire --expire=now --all; git gc --prune=now --aggressive
 git push origin --force --all
 git push origin --force --tags

4) Verify the secret is removed
 git rev-list --all --objects | Select-String 'serviceAccountKey.json'

If the search prints nothing, the file path is no longer in history.

5) If GitHub push protection still blocks the push
- Visit the security link shown in the push error and follow instructions to request an unblock if necessary.
- If your organization requires an admin to allow the push, contact the repo admins with proof you removed the secret and rotated credentials.

6) Additional recommendations
- Use environment variables or a secrets manager for credentials; never commit keys.
- Add a pre-commit hook with `pre-commit` and the `detect-secrets` plugin to prevent future secrets from being committed.

If you want, I can create a PowerShell helper script that runs the verification commands (non-destructive) and a sample pre-commit config to catch secrets before commits.

-- Repository Security Bot
