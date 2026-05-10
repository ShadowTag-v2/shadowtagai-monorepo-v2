export function feature(flagName: string): boolean {
  switch (flagName) {
    case 'ant_user':
      return process.env.USER_TYPE === 'ant';
    case 'development':
      return process.env.NODE_ENV === 'development';
    case 'test':
      return process.env.NODE_ENV === 'test';
    default:
      return false;
  }
}
