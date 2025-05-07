#!/bin/bash

cd /Users/sea/Documents/dev/superapp || exit 1

# Ensure we're on the main branch
git checkout main

# Stage and commit changes
git add .
git commit -m "Daily update: $(date '+%Y-%m-%d')" || echo "No changes to commit."

# Pull + rebase just in case something changed upstream
git pull --rebase origin main

# Push to GitHub
git push origin main
