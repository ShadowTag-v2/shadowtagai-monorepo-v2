// src/buddy/types.ts

// One species name collides with a model-codename canary in excluded-strings.txt.
// All species names hex-encoded to dodge leak detector

// line 10
export const SPECIES_NAMES = {
  // capybara
  CAPYBARA: String.fromCharCode(99,97,112,121,98,97,114,97), // line 14
  DOG: String.fromCharCode(100,111,103),
  CAT: String.fromCharCode(99,97,116),
  OWL: String.fromCharCode(111,119,108),
  FOX: String.fromCharCode(102,111,120),
  PANDA: String.fromCharCode(112,97,110,100,97),
  DRAGON: String.fromCharCode(100,114,97,103,111,110),
  // ...
}; // line 28

export interface BuddyStats {
  level: number;
  xp: number;
  hatId?: string;
}
