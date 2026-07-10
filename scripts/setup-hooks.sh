#!/bin/sh
# Point git at the committed hooks so `main` is protected locally (PR-only). Run once per checkout.
#   sh scripts/setup-hooks.sh
set -e
git config core.hooksPath .githooks
chmod +x .githooks/* 2>/dev/null || true
echo "✅ hooks installed (core.hooksPath=.githooks). Direct pushes to main are now blocked here."
echo "   Emergency override for one push: ALLOW_MAIN_PUSH=1 git push"
