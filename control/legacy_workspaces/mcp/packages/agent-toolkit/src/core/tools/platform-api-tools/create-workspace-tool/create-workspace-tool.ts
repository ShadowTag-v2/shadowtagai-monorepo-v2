import { z } from "zod";
import {
  type CreateWorkspaceMutation,
  type CreateWorkspaceMutationVariables,
  WorkspaceKind,
} from "../../../../monday-graphql/generated/graphql/graphql";
import { type ToolInputType, type ToolOutputType, ToolType } from "../../../tool";
import { BaseMondayApiTool, createMondayApiAnnotations } from "../base-monday-api-tool";
import { createWorkspace } from "./create-workspace-tool.graphql";

export const createWorkspaceToolSchema = {
  name: z.string().describe("The name of the new workspace to be created"),
  workspaceKind: z.nativeEnum(WorkspaceKind).describe("The kind of workspace to create"),
  description: z.string().optional().describe("The description of the new workspace"),
  accountProductId: z
    .string()
    .optional()
    .describe("The account product ID associated with the workspace"),
};

export type CreateWorkspaceToolInput = typeof createWorkspaceToolSchema;

export class CreateWorkspaceTool extends BaseMondayApiTool<CreateWorkspaceToolInput> {
  name = "create_workspace";
  type = ToolType.WRITE;
  annotations = createMondayApiAnnotations({
    title: "Create Workspace",
    readOnlyHint: false,
    destructiveHint: false,
    idempotentHint: false,
  });

  getDescription(): string {
    return "Create a new workspace in monday.com";
  }

  getInputSchema(): CreateWorkspaceToolInput {
    return createWorkspaceToolSchema;
  }

  protected async executeInternal(
    input: ToolInputType<CreateWorkspaceToolInput>,
  ): Promise<ToolOutputType<never>> {
    const variables: CreateWorkspaceMutationVariables = {
      name: input.name,
      workspaceKind: input.workspaceKind,
      description: input.description,
      accountProductId: input.accountProductId,
    };

    const res = await this.mondayApi.request<CreateWorkspaceMutation>(createWorkspace, variables);

    return {
      content: `Workspace ${res.create_workspace?.id} successfully created`,
    };
  }
}
