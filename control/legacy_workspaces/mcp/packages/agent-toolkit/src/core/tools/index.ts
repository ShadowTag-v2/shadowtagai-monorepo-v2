import { allMondayAppsTools } from "./monday-apps-tools";
import { allMondayDevTools } from "./monday-dev-tools";
import { allGraphqlApiTools } from "./platform-api-tools";

export const allTools = [...allGraphqlApiTools, ...allMondayDevTools, ...allMondayAppsTools];

export { allGraphqlApiTools, allMondayAppsTools, allMondayDevTools };
