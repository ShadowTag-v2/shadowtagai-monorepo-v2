import type { ZodCatchDef } from "zod/v3";
import { parseDef } from "../parseDef";
import type { Refs } from "../Refs";

export const parseCatchDef = (def: ZodCatchDef<any>, refs: Refs) => {
  return parseDef(def.innerType._def, refs);
};
