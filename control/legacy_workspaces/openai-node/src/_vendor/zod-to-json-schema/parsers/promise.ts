import type { ZodPromiseDef } from "zod/v3";
import { type JsonSchema7Type, parseDef } from "../parseDef";
import type { Refs } from "../Refs";

export function parsePromiseDef(def: ZodPromiseDef, refs: Refs): JsonSchema7Type | undefined {
  return parseDef(def.type._def, refs);
}
