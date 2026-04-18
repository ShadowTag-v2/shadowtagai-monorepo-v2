using System;
using System.Threading.Tasks;
// Note: In a real project, we would reference the Mcp.Sdk (conceptually similar to the Python one)
// For this Gold Master file, we assume the necessary MCP abstractions are present.

namespace SeatJudge.Inventory.Mcp;

public class Program
{
    public static async Task Main(string[] args)
    {
        // The "USB-C" for our AI
        var server = new McpServer("SeatJudge.Inventory", "1.0.0");

        // Mock Redis client for the example
        var redis = new MockRedisClient();

        server.AddTool(new Tool("lock_table", "Locks a table for 90s (Optimistic)")
        {
            Parameters = new { table_id = "string", user_id = "string" },
            Handler = async (toolArgs) => {
                // Direct Redis Call
                // In production: var db = ConnectionMultiplexer.Connect("...").GetDatabase();
                var tableId = toolArgs["table_id"]?.ToString();
                var userId = toolArgs["user_id"]?.ToString();

                if (string.IsNullOrEmpty(tableId) || string.IsNullOrEmpty(userId))
                    return "ERROR: Missing parameters";

                var success = await redis.StringSetAsync($"lock:{tableId}", userId, TimeSpan.FromSeconds(90));
                return success ? "LOCKED" : "CONFLICT";
            }
        });

        Console.WriteLine("SeatJudge Inventory MCP Server Running...");
        await server.StartAsync();
    }
}

// ---------------------------------------------------------
// MOCKS & STUBS (For Self-Contained Compilation)
// ---------------------------------------------------------

public class McpServer(string name, string version)
{
    public void AddTool(Tool tool) { /* Register tool */ }
    public Task StartAsync() { /* Start stdio loop */ return Task.CompletedTask; }
}

public class Tool(string name, string description)
{
    public object Parameters { get; set; }
    public Func<System.Collections.Generic.Dictionary<string, object>, Task<string>> Handler { get; set; }
}

public class MockRedisClient
{
    public Task<bool> StringSetAsync(string key, string value, TimeSpan expiry)
    {
        // Simulate success
        return Task.FromResult(true);
    }
}
