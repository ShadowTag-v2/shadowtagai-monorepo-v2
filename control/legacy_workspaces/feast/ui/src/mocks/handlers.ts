import { readFileSync } from "fs";
import { HttpResponse, http } from "msw";
import path from "path";

const registry = readFileSync(path.resolve(__dirname, "../../public/registry.db"));

const projectsListWithDefaultProject = http.get("/projects-list.json", () =>
  HttpResponse.json({
    default: "credit_scoring_aws",
    projects: [
      {
        name: "Credit Score Project",
        description: "Project for credit scoring team and associated models.",
        id: "credit_scoring_aws",
        registryPath: "/registry.db", // Changed to match what the test expects
      },
    ],
  }),
);

const creditHistoryRegistryPB = http.get("/registry.pb", () => {
  return HttpResponse.arrayBuffer(registry.buffer);
});

const creditHistoryRegistryDB = http.get("/registry.db", () => {
  return HttpResponse.arrayBuffer(registry.buffer);
});

export {
  creditHistoryRegistryDB,
  creditHistoryRegistryPB as creditHistoryRegistry,
  projectsListWithDefaultProject,
};
