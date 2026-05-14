import type { ZodDefaultDef } from "zod/v3";
import { type JsonSchema7Type, parseDef } from "../parseDef";
import type { Refs } from "../Refs";

export function parseDefaultDef(
  _def: ZodDefaultDef,
  refs: Refs,
): JsonSchema7Type & { default: any } {
  return {
    ...parseDef(_def.innerType._def, refs),
    default: _def.defaultValue(),
  };
}
