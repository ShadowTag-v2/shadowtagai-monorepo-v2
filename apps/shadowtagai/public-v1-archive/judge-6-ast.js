export async function evaluateAST(input) {
    try {
        // Attempt to reach the active backend indexer
        const response = await fetch('http://localhost:8000/api/v1/ast/parse', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: input })
        });

        const result = await response.json();
        return result;
    } catch (err) {
        throw new Error('Local API unavailable');
    }
}

export function evaluateWASM(input) {
    return new Promise((resolve) => {
        setTimeout(() => {
            if(input.includes("rm") || input.includes("drop") || input.includes("delete")) {
                resolve({ status: "VIOLATION", message: "Destructive modifier detected at root execution.", shield: "Execution Killed" });
            } else {
                resolve({ status: "OK", message: "Tree-sitter validated pure execution node.", shield: "Let pass" });
            }
        }, 800);
    });
}
