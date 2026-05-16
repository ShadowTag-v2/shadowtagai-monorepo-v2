import type { DisplayMode } from "./types";
import { useOpenAiGlobal } from "./useOpenAiGlobal";

export const useDisplayMode = (): DisplayMode | null => {
  return useOpenAiGlobal("displayMode");
};
