using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using StackExchange.Redis;

// Note: In a real project, we would reference the Mcp.Sdk (conceptually similar to the Python one)
// For this Gold Master file, we assume the necessary MCP abstractions are present.

namespace SeatJudge.Inventory.Mcp;

public class Program
{
    public static async Task Main(string[] args)
    {
        // The "USB-C" for our AI
        var server = new McpServer("SeatJudge.Inventory", "1.0.0");

        // Real Redis client
        // In a real scenario, connection string should come from config/env
        var connectionString = Environment.GetEnvironmentVariable("REDIS_CONNECTION_STRING") ?? "localhost";
        using var redis = await ConnectionMultiplexer.ConnectAsync(connectionString);
        var db = redis.GetDatabase();

        // ── Tool 1: Lock Table ──────────────────────────────────
        server.AddTool(new Tool("lock_table", "Locks a table for 90s (Optimistic)")
        {
            Parameters = new { table_id = "string", user_id = "string" },
            Handler = async (toolArgs) => {
                var tableId = toolArgs.GetValueOrDefault("table_id")?.ToString();
                var userId = toolArgs.GetValueOrDefault("user_id")?.ToString();

                if (string.IsNullOrEmpty(tableId) || string.IsNullOrEmpty(userId))
                    return "ERROR: Missing parameters";

                // Optimistic locking with a 90s expiration
                var success = await db.StringSetAsync($"lock:{tableId}", userId, TimeSpan.FromSeconds(90), When.NotExists);
                return success ? "LOCKED" : "CONFLICT";
            }
        });

        // ── Tool 2: Unlock Table ────────────────────────────────
        server.AddTool(new Tool("unlock_table", "Releases a lock on a table. Only the user who locked it can unlock.")
        {
            Parameters = new { table_id = "string", user_id = "string" },
            Handler = async (toolArgs) => {
                var tableId = toolArgs.GetValueOrDefault("table_id")?.ToString();
                var userId = toolArgs.GetValueOrDefault("user_id")?.ToString();

                if (string.IsNullOrEmpty(tableId) || string.IsNullOrEmpty(userId))
                    return "ERROR: Missing parameters";

                var currentHolder = await db.StringGetAsync($"lock:{tableId}");
                if (currentHolder.IsNull)
                    return "NOT_LOCKED";
                if (currentHolder.ToString() != userId)
                    return "FORBIDDEN: Lock held by another user";

                await db.KeyDeleteAsync($"lock:{tableId}");
                return "UNLOCKED";
            }
        });

        // ── Tool 3: Check Availability ──────────────────────────
        server.AddTool(new Tool("check_availability", "Checks if a table is available or locked. Returns status and holder.")
        {
            Parameters = new { table_id = "string" },
            Handler = async (toolArgs) => {
                var tableId = toolArgs.GetValueOrDefault("table_id")?.ToString();

                if (string.IsNullOrEmpty(tableId))
                    return "ERROR: Missing table_id";

                var holder = await db.StringGetAsync($"lock:{tableId}");
                var ttl = await db.KeyTimeToLiveAsync($"lock:{tableId}");

                if (holder.IsNull)
                    return $"AVAILABLE: Table {tableId} is free";

                return $"LOCKED: Table {tableId} held by {holder} (expires in {ttl?.TotalSeconds:F0}s)";
            }
        });

        // ── Tool 4: List Tables ─────────────────────────────────
        server.AddTool(new Tool("list_tables", "Lists all known tables and their lock status. Scans Redis for lock:* keys.")
        {
            Parameters = new { prefix = "string?" },
            Handler = async (toolArgs) => {
                var prefix = toolArgs.GetValueOrDefault("prefix")?.ToString() ?? "";
                var results = new List<string>();
                var endpoints = redis.GetEndPoints();
                var serverInstance = redis.GetServer(endpoints[0]);

                await foreach (var key in serverInstance.KeysAsync(pattern: $"lock:{prefix}*", pageSize: 100))
                {
                    var holder = await db.StringGetAsync(key);
                    var ttl = await db.KeyTimeToLiveAsync(key);
                    var tableId = key.ToString().Replace("lock:", "");
                    results.Add($"  {tableId}: locked by {holder} (TTL: {ttl?.TotalSeconds:F0}s)");
                }

                if (results.Count == 0)
                    return "No tables currently locked.";

                return $"Locked tables ({results.Count}):\n{string.Join("\n", results)}";
            }
        });

        // ── Tool 5: Batch Lock ──────────────────────────────────
        server.AddTool(new Tool("batch_lock", "Atomically locks multiple tables for a reservation. All-or-nothing.")
        {
            Parameters = new { table_ids = "string[]", user_id = "string" },
            Handler = async (toolArgs) => {
                var userId = toolArgs.GetValueOrDefault("user_id")?.ToString();
                var tableIdsRaw = toolArgs.GetValueOrDefault("table_ids")?.ToString();

                if (string.IsNullOrEmpty(userId) || string.IsNullOrEmpty(tableIdsRaw))
                    return "ERROR: Missing parameters";

                var tableIds = tableIdsRaw.Split(',').Select(t => t.Trim()).ToArray();
                var locked = new List<string>();

                try
                {
                    // Phase 1: Attempt to lock all
                    foreach (var tableId in tableIds)
                    {
                        var success = await db.StringSetAsync($"lock:{tableId}", userId, TimeSpan.FromSeconds(90), When.NotExists);
                        if (!success)
                        {
                            // Rollback: unlock all previously locked in this batch
                            foreach (var lockedId in locked)
                                await db.KeyDeleteAsync($"lock:{lockedId}");

                            return $"CONFLICT: Table {tableId} is already locked. Batch rolled back.";
                        }
                        locked.Add(tableId);
                    }

                    return $"BATCH_LOCKED: {locked.Count} tables locked for {userId}";
                }
                catch (Exception ex)
                {
                    // Rollback on error
                    foreach (var lockedId in locked)
                        await db.KeyDeleteAsync($"lock:{lockedId}");

                    return $"ERROR: {ex.Message}. Batch rolled back.";
                }
            }
        });

        Console.WriteLine("SeatJudge Inventory MCP Server Running...");
        Console.WriteLine("Tools registered: lock_table, unlock_table, check_availability, list_tables, batch_lock");
        await server.StartAsync();
    }
}

// ---------------------------------------------------------
// MOCKS & STUBS (For Self-Contained Compilation)
// ---------------------------------------------------------

public class McpServer(string name, string version)
{
    public string Name { get; } = name;
    public string Version { get; } = version;

    public void AddTool(Tool tool)
    {
        Console.WriteLine($"Registered tool: {tool.Name}");
    }

    public async Task StartAsync()
    {
        // Simulate a running server loop
        Console.WriteLine($"Starting {Name} v{Version}...");
        await Task.Delay(-1); // Block indefinitely
    }
}

public class Tool(string name, string description)
{
    public string Name { get; } = name;
    public string Description { get; } = description;

    public required object Parameters { get; set; }
    public required Func<Dictionary<string, object>, Task<string>> Handler { get; set; }
}
