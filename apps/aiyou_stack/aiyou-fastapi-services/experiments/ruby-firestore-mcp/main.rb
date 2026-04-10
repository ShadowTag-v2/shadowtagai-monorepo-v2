require 'bundler/setup'
require 'mcp_sdk'
require 'google/cloud/firestore'
require_relative 'lib/inventory_tool'

# Initialize Firestore
firestore = Google::Cloud::Firestore.new(project_id: ENV['PROJECT_ID'])

# Initialize MCP Server
server = MCP::Server.new(name: "firestore-ruby-mcp", version: "1.0.0")

# Register Tools
server.register_tool(InventoryTool.new(firestore))

# Start Server (Stdio or HTTP based on ENV)
if ENV['MCP_TRANSPORT'] == 'http'
  require 'rack'
  require 'rack/handler/puma'
  
  puts "Starting Ruby MCP Server on port 8080..."
  Rack::Handler::Puma.run(server.rack_app, Port: 8080, Host: '0.0.0.0')
else
  puts "Starting Ruby MCP Server (Stdio)..."
  server.start_stdio
end
