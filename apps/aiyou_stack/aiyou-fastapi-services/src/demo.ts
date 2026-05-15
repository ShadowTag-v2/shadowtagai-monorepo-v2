// EXPECT 3 violations:
const mod = await import('./x'); // dynamic import
const v: unknown = 42; // any
try {
  // useless try/catch
  console.log(v, mod);
} catch (e) {}
