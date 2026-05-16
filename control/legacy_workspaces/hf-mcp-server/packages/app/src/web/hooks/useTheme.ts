import type { Theme } from "./types";
import { useOpenAiGlobal } from "./useOpenAiGlobal";

export const useTheme = (): Theme | null => {
  return useOpenAiGlobal("theme");
};
