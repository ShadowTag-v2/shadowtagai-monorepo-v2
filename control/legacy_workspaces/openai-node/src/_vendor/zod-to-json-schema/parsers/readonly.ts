import type { ZodReadonlyDef } from "zod/v3";
import { parseDef } from "../parseDef";
import type { Refs } from "../Refs";

export const parseReadonlyDef = (def: ZodReadonlyDef<any>, refs: Refs) => {
  return parseDef(def.innerType._def, refs);
};
