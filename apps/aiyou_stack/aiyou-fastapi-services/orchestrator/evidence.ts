export async function buildCase(inputs: unknown) {
  return {
    id: "case_" + Date.now(),
    inputs,
    artifacts: [],
  };
}
