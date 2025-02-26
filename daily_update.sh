#!/bin/bash

# Navigate to your local project directory (adjust the path as needed)
cd /Users/sea/Documents/dev/superapp

# Use the stored GitHub token
GIT_USERNAME="motherdomains"
GIT_REPO="github.com/motherdomains/superagency.git"

git remote set-url origin https://$GITHUB_TOKEN@$GIT_REPO

# Stage all changes (new, modified, deleted files)
git add .

# Commit the changes with a message containing the date
git commit -m "Daily update: $(date '+%Y-%m-%d')"

# Push the changes to the remote repository
git push origin main
