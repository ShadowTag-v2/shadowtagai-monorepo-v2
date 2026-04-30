{
  "name": "vercel_dynamic_skills_cli",
  "description": "Utilizes the Vercel Agent Skills CLI (npx skills) to dynamically discover or execute atomic web-development capabilities without requiring hardcoded backend tools.",
  "parameters": {
    "type": "object",
    "properties": {
      "action": {
        "type": "string",
        "enum": ["discover", "execute"],
        "description": "Whether to search the registry for a new skill ('discover') or run a known skill ('execute')."
      },
      "query_or_skill_name": {
        "type": "string",
        "description": "If discovering, the natural language query (e.g., 'check seo'). If executing, the exact skill name (e.g., 'a11y-audit')."
      },
      "cli_arguments": {
        "type": "string",
        "description": "If executing, the CLI arguments to pass to the skill (e.g., '--target ./src'). Leave empty for discovery."
      }
    },
    "required": ["action", "query_or_skill_name"]
  },
  "system_instruction": "When action is 'discover', execute 'npx -y skills --skill find-skills --query <query>' via bash. When 'execute', execute 'npx -y skills --skill <skill_name> <cli_arguments>' via bash."
}
