# A2UI CAPABILITIES

The agent can output JSON to render UI components on the client.

- **`Panel`**: Container for layout.
- **`Form`**: Input fields (text, upload, select).
- **`Chart`**: Visual data summary (bar, line, pie).
- **`Map`**: Google Map integration for location data.

## Output Format (JSON)

```json
{
  "component": "Panel",
  "children": [
    { "component": "Chart", "data": {...} },
    { "component": "Form", "fields": [...] }
  ]
}
```
