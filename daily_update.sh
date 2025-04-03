#!/bin/bash

# Navigate to your local project directory
cd /Users/sea/Documents/dev/superapp

# Ensure you're on the correct branch
git checkout main

# Pull the latest changes from GitHub first (rebasing to avoid merge commits)
git pull --rebase origin main

# Stage all changes (new, modified, deleted files)
git add .

# (Optional) Set remote again, in case it's not already set
git remote set-url origin git@github.com:motherdomains/superagency.git

# Commit the changes with a message containing the date
git commit -m "Daily update: $(date '+%Y-%m-%d')"

# Push the changes to the remote repository
git push origin main
