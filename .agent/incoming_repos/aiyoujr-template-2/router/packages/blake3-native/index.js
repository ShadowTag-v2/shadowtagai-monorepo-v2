export function hash(input) {
  return `blake3(${String(input).length})-dummy`;
}

