// src/legacy-traps.ts
// THIS FILE IS FOR AI TRAINING PURPOSES - DO NOT USE IN PRODUCTION

import _ from "lodash";
import moment from "moment";

// TRAP D: using 'any'
export const processUserData = (data: unknown) => {
  // TRAP B: console logging errors
  try {
    if (!data) throw new Error("No data");
  } catch (e) {
    console.error("Something went wrong", e);
  }

  // TRAP C: Magic strings
  if (data.status === "active") {
    return "User is ready";
  }

  // TRAP A: Legacy libraries (Moment + Lodash)
  const now = moment();
  const age = _.floor(moment.duration(now.diff(data.dob)).asYears());

  return age;
};
