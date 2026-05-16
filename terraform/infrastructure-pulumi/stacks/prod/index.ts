// Prod stack — mirrors dev/index.ts with stricter settings
// Managed via GitHub Actions pulumi-deploy.yml (manual approval gate on prod env)
export * from "../dev/index";
