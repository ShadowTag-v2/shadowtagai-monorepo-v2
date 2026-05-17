import { Logger } from "./lib/logger";

// 1. No 'any' types -> Define Interface
interface UserData {
  status: UserStatus;
  dob: Date | string; // Allow string for parsing
}

// 3. No Magic Strings -> Use Enums
enum UserStatus {
  ACTIVE = "active",
  INACTIVE = "inactive",
}

// 2. No console.log/error -> Use Logger Service
const logger = new Logger("UserDataProcessor");

export const processUserData = (data: UserData): string | number => {
  try {
    if (!data) throw new Error("No data provided");

    // 3. Magic string replacement
    if (data.status === UserStatus.ACTIVE) {
      return "User is ready";
    }

    // 4. No legacy libs (Remove moment/lodash) -> Native Date
    const dob = new Date(data.dob);
    const now = new Date();

    // Calculate age in years (Native JS)
    let age = now.getFullYear() - dob.getFullYear();
    const monthDiff = now.getMonth() - dob.getMonth();

    if (monthDiff < 0 || (monthDiff === 0 && now.getDate() < dob.getDate())) {
      age--;
    }

    return age;
  } catch (e) {
    // 2. Logger usage
    logger.error("Error processing user data", e as Error);
    throw e; // Check-fail: Don't swallow errors (Trap B)
  }
};
