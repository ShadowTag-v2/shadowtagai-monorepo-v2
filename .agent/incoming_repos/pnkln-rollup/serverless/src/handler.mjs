export async function hello(event) {
  const message = "pnkln serverless starter online";
  return {
    statusCode: 200,
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ message, time: new Date().toISOString() }),
  };
}

export async function insertThought(event) {
  // Inputs: { label: string, embedding: number[] }
  try {
    const body = event?.body ? JSON.parse(event.body) : {};
    const { label, embedding } = body || {};
    const dim = Number(process.env.VECTOR_DIM || "384");
    if (!Array.isArray(embedding) || embedding.length !== dim || typeof label !== "string") {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: "Invalid input: label and embedding[dim] required" }),
      };
    }
    const { Client } = await import("pg");
    const client = new Client({
      host: process.env.PG_HOST,
      port: Number(process.env.PG_PORT || "5432"),
      user: process.env.PG_USER,
      password: process.env.PG_PASSWORD,
      database: process.env.PG_DATABASE,
      ssl: process.env.PG_SSL === "true" ? { rejectUnauthorized: false } : undefined,
    });
    await client.connect();
    const vectorLiteral = "[" + embedding.join(",") + "]";
    const res = await client.query(
      "INSERT INTO thoughts(label, embedding) VALUES ($1, $2::vector) RETURNING id, created_at",
      [label, vectorLiteral],
    );
    await client.end();
    return {
      statusCode: 201,
      body: JSON.stringify({ id: res.rows[0]?.id, createdAt: res.rows[0]?.created_at }),
    };
  } catch (err) {
    return {
      statusCode: 500,
      body: JSON.stringify({
        error: "Insert failed",
        details: String((err && err.message) || err),
      }),
    };
  }
}
