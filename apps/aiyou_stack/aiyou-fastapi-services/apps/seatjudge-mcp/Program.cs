using System;
using System.Collections.Generic;
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

        Console.WriteLine("SeatJudge Inventory MCP Server Running...");
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
