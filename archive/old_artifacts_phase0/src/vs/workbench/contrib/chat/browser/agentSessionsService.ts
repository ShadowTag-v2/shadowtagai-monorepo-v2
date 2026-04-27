import { registerSingleton, InstantiationType } from 'vs/platform/instantiation/common/extensions';
import { IAgentSessionsService } from './agentSessionsService';
import { AgentSessionsService } from './agentSessionsServiceImpl';
registerSingleton(IAgentSessionsService, AgentSessionsService, InstantiationType.Delayed);
