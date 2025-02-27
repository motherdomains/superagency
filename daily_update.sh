#!/bin/bash

# Navigate to your local project directory (adjust the path as needed)
cd /Users/sea/Documents/dev/superapp

# Use the stored GitHub token
GIT_USERNAME="motherdomains"
GITHUB_TOKEN="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"
GIT_REPO="github.com/motherdomains/superagency.git"

# Stage all changes (new, modified, deleted files)
git add .

# Commit the changes with a message containing the date
git commit -m "Daily update: $(date '+%Y-%m-%d')"

# Push the changes to the remote repository
git push origin main
