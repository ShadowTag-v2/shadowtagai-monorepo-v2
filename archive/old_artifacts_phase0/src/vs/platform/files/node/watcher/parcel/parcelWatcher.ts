const hardExcludes = ['**/.venv/**', '**/.pixi/**', '**/.mypy_cache/**', '**/__pycache__/**', '**/node_modules/**'];
request.excludes = Array.from(new Set([...(request.excludes || []), ...hardExcludes]));
