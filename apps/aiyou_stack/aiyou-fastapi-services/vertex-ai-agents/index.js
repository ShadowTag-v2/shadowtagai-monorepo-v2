/**
 * Vertex AI Agents Registry
 * Main entry point for loading and managing AI agents
 */

const fs = require("fs").promises;
const path = require("path");

class AgentRegistry {
  constructor() {
    this.agents = new Map();
    this.categories = new Map();
    this.loaded = false;
  }

  /**
   * Load all agents from the registry
   */
  async loadAgents() {
    if (this.loaded) return;

    try {
      const registryPath = path.join(__dirname, "registry.json");
      const registryData = await fs.readFile(registryPath, "utf8");
      const registry = JSON.parse(registryData);

      // Load each category
      for (const [categoryId, categoryData] of Object.entries(registry.categories)) {
        this.categories.set(categoryId, {
          ...categoryData,
          id: categoryId,
        });

        // Load each agent in the category
        for (const agentId of categoryData.agents) {
          const agentPath = path.join(__dirname, categoryId, `${agentId}.json`);
          try {
            const agentData = await fs.readFile(agentPath, "utf8");
            const agent = JSON.parse(agentData);
            this.agents.set(agentId, {
              ...agent,
              categoryId,
            });
          } catch (error) {
            console.warn(`Failed to load agent ${agentId}:`, error.message);
          }
        }
      }

      this.loaded = true;
      console.log(`Loaded ${this.agents.size} agents across ${this.categories.size} categories`);
    } catch (error) {
      console.error("Failed to load agent registry:", error);
      throw error;
    }
  }

  /**
   * Get an agent by ID
   */
  getAgent(agentId) {
    return this.agents.get(agentId);
  }

  /**
   * Get all agents
   */
  getAllAgents() {
    return Array.from(this.agents.values());
  }

  /**
   * Get agents by category
   */
  getAgentsByCategory(categoryId) {
    return this.getAllAgents().filter((agent) => agent.categoryId === categoryId);
  }

  /**
   * Get all categories
   */
  getAllCategories() {
    return Array.from(this.categories.values());
  }

  /**
   * Search agents by keyword
   */
  searchAgents(keyword) {
    const lowerKeyword = keyword.toLowerCase();
    return this.getAllAgents().filter((agent) => {
      return (
        agent.name.toLowerCase().includes(lowerKeyword) ||
        agent.description.toLowerCase().includes(lowerKeyword) ||
        agent.capabilities.some((cap) => cap.toLowerCase().includes(lowerKeyword))
      );
    });
  }

  /**
   * Get agent recommendations based on use case
   */
  recommendAgents(useCase) {
    const lowerUseCase = useCase.toLowerCase();
    return this.getAllAgents().filter((agent) => {
      return agent.useCases.some((uc) => uc.toLowerCase().includes(lowerUseCase));
    });
  }
}

// Singleton instance
const registry = new AgentRegistry();

module.exports = {
  AgentRegistry,
  registry,

  // Convenience exports
  loadAgents: () => registry.loadAgents(),
  getAgent: (id) => registry.getAgent(id),
  getAllAgents: () => registry.getAllAgents(),
  getAgentsByCategory: (categoryId) => registry.getAgentsByCategory(categoryId),
  getAllCategories: () => registry.getAllCategories(),
  searchAgents: (keyword) => registry.searchAgents(keyword),
  recommendAgents: (useCase) => registry.recommendAgents(useCase),
};
