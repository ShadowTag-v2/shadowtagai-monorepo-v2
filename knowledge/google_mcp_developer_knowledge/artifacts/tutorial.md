# Mastering the Google Developer Knowledge MCP Server

If your Google Developer Knowledge API or its associated MCP Server isn't working as expected, there are a few standard troubleshooting paths you can take to identify and resolve the issue.

The first step in any troubleshooting process should be to ensure you are meeting the basic prerequisites and using the correct configuration.
Ensure that the Cloud Project has the correct billing enabled.
Ensure that the Google Developer Knowledge API is enabled.
Ensure that the Google Maps API is enabled.
Ensure that the proper roles are applied to the service account or authenticated user invoking the API.
Double check your gemini-cli-settings.json file or the config file for whatever IDE you are using and ensure your API key or Google Application Default Credentials are correct.

Once you have validated the configuration, you can use the MCP Inspector tool to test tool endpoints.
See https://modelcontextprotocol.io/docs/tools/inspector for instructions on using the inspector.

If you are encountering errors, review the MCP Debugging Documentation at https://modelcontextprotocol.io/docs/tools/debugging.
Common issues include network routing, missing IAM roles, and rate limiting by the underlying Developer Knowledge APIs.

If you continue to experience problems after checking these basics, you can search for existing issues or report a new one on the Google Developer Knowledge Issue Tracker.
