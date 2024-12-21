#!/bin/bash

# Navigate to your local project directory (adjust the path as needed)
cd /Users/sea/Documents/dev/superapp

# Stage all changes (new, modified, deleted files)
git add .

# Commit the changes with a message containing the date
git commit -m "Daily update: $(date '+%Y-%m-%d')"

# Push the changes to the remote repository
git push origin main