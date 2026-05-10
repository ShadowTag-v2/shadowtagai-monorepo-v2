#!/bin/bash
echo "🧠 [Phase 3] The Surgeon: Refactoring Imports..."

# 1. Establish the Lib Config
if [ -d "libs/utils" ]; then
    cat > libs/utils/pyproject.toml <<EOF
[project]
name = "libs-utils"
version = "0.1.0"
dependencies = []
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
EOF
fi

# 2. Perform the Surgery
# We look for "from utils" and "import utils" in python files inside apps/
echo "   -> Rewiring 'utils' to 'libs.utils'..."
find apps -type f -name "*.py" -print0 | xargs -0 sed -i '' 's/^from utils/from libs.utils/g'
find apps -type f -name "*.py" -print0 | xargs -0 sed -i '' 's/^import utils/import libs.utils/g'

# 3. Handle 'core' if it exists
if [ -d "libs/core" ]; then
    echo "   -> Rewiring 'core' to 'libs.core'..."
    find apps -type f -name "*.py" -print0 | xargs -0 sed -i '' 's/^from core/from libs.core/g'
    find apps -type f -name "*.py" -print0 | xargs -0 sed -i '' 's/^import core/import libs.core/g'
fi

# 4. Fix Relative Imports in moved apps
# If 'ungpt' code had 'from agents import X', it might now need fixing if folder structure inside changed.
# For now, we assume internal app structure was preserved during the move.

echo "✅ [Phase 3] Surgery Complete."
