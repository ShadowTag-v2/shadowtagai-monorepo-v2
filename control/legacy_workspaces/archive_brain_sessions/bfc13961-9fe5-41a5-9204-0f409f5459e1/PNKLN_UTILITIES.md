# PNKLN UTILITIES & SCRIPTS (Cor.50 + Cor.61 Archive)

## 1. "Vibe Coding" Hooks Configuration
```json
// .claude/skills/skill-rules.json
{
  "backend-dev-guidelines": {
    "type": "domain",
    "enforcement": "suggest",
    "promptTriggers": {
      "keywords": ["backend", "API", "controller"],
      "intentPatterns": ["(create|add).*?(route|endpoint)"]
    },
    "fileTriggers": {
      "pathPatterns": ["backend/src/**/*.ts"]
    }
  }
}
```

## 2. PM2 Ecosystem Config
```javascript
// ecosystem.config.js
module.exports = {
  apps: [
    {
      name: 'yougle-api',
      script: 'uv',
      args: 'run start_api.py',
      cwd: './apps/yougle-api',
      error_file: './logs/api-err.log',
      out_file: './logs/api-out.log'
    },
    {
      name: 'router-service',
      script: 'npm',
      args: 'start',
      cwd: './services/router'
    }
  ]
};
```

## 3. Run1 / Run2 / Run3 Loop (Python Stub)
*(Retained from Cor.31)*
```python
# services/orchestrator-langchain/run_cycles.py
# Run1 (Gen) -> Run2 (Explain) -> Run3 (Challenge)
# ...
```

## 4. Yougle API Stub
*(Retained from Cor.31)*
```python
# apps/yougle-api/main.py
# ...
```

## 5. Cursor Plan Mode Rules
*(Retained from Cor.32)*
```json
{
  "rules": ["Sacrifice grammar", "One action per line"]
}
```
