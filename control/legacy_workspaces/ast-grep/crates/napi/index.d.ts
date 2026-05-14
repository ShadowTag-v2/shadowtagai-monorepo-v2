// -----Type Only Export!-----//

// -----Runtime Value Export!-----//
export { findInFiles, kind, parse, parseAsync, parseFiles, pattern } from "./types/api";
export type { FileOption, FindConfig, NapiConfig } from "./types/config";
// deprecated
export * from "./types/deprecated";
export { Lang } from "./types/lang";
export type { DynamicLangRegistrations } from "./types/registerDynamicLang";
export { registerDynamicLanguage } from "./types/registerDynamicLang";
// Only Rule here. User can use Rule['pattern'], e.g., to get the type of subfield.
export type { Rule } from "./types/rule";
export type { Edit, Pos, Range } from "./types/sgnode";
export { SgNode, SgRoot } from "./types/sgnode";
