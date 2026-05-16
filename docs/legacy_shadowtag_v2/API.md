# API Documentation

Complete API reference for pnkln-stack FastAPI Services Checkpointing.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

Currently, the API does not require authentication. In production, implement appropriate authentication mechanisms.

## Endpoints

### Health Check

#### GET /health

Check service health status.

**Response:**
```json
{
  "status": "healthy"
}
```

---

### Checkpoints

#### POST /checkpoints

Create a new checkpoint.

**Request Body:**
```json
{
  "session_id": "string",
  "user_message": "string (optional)",
  "checkpoint_type": "auto | manual",
  "file_paths": ["string"],
  "metadata": {} (optional)
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "session_id": "string",
  "user_message": "string",
  "checkpoint_type": "auto",
  "status": "active",
  "created_at": "2024-01-15T10:30:00",
  "restored_at": null,
  "expires_at": "2024-02-14T10:30:00",
  "file_count": 3,
  "total_size_bytes": 15420,
  "metadata": {}
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/checkpoints \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session_123",
    "user_message": "Before refactoring auth",
    "checkpoint_type": "auto",
    "file_paths": ["/app/auth.py", "/app/models.py"]
  }'
```

---

#### GET /checkpoints/{checkpoint_id}

Get checkpoint details by ID.

**Parameters:**
- `checkpoint_id` (path) - Checkpoint identifier

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "session_id": "string",
  "user_message": "string",
  "checkpoint_type": "auto",
  "status": "active",
  "created_at": "2024-01-15T10:30:00",
  "restored_at": null,
  "expires_at": "2024-02-14T10:30:00",
  "file_count": 3,
  "total_size_bytes": 15420,
  "metadata": {}
}
```

**Errors:**
- `404 Not Found` - Checkpoint not found

**Example:**
```bash
curl http://localhost:8000/api/v1/checkpoints/{checkpoint_id}
```

---

#### GET /checkpoints/sessions/{session_id}

List all checkpoints for a session.

**Parameters:**
- `session_id` (path) - Session identifier
- `limit` (query, optional) - Maximum results (default: 100)
- `offset` (query, optional) - Results to skip (default: 0)

**Response:** `200 OK`
```json
{
  "checkpoints": [
    {
      "id": "uuid",
      "session_id": "string",
      "user_message": "string",
      "checkpoint_type": "auto",
      "status": "active",
      "created_at": "2024-01-15T10:30:00",
      "restored_at": null,
      "expires_at": "2024-02-14T10:30:00",
      "file_count": 3,
      "total_size_bytes": 15420,
      "metadata": {}
    }
  ],
  "total": 10,
  "session_id": "session_123"
}
```

**Example:**
```bash
curl "http://localhost:8000/api/v1/checkpoints/sessions/session_123?limit=10&offset=0"
```

---

#### POST /checkpoints/{checkpoint_id}/restore

Restore a checkpoint.

**Parameters:**
- `checkpoint_id` (path) - Checkpoint identifier

**Request Body:**
```json
{
  "restore_code": true,
  "restore_conversation": false
}
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "session_id": "string",
  "status": "restored",
  "restored_at": "2024-01-15T11:00:00",
  ...
}
```

**Errors:**
- `404 Not Found` - Checkpoint not found or expired
- `500 Internal Server Error` - Restore failed

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/checkpoints/{checkpoint_id}/restore \
  -H "Content-Type: application/json" \
  -d '{"restore_code": true, "restore_conversation": false}'
```

---

#### GET /checkpoints/{checkpoint_id}/files

Get all file snapshots for a checkpoint.

**Parameters:**
- `checkpoint_id` (path) - Checkpoint identifier

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "checkpoint_id": "uuid",
    "file_path": "/app/auth.py",
    "content_hash": "sha256_hash",
    "size_bytes": 5420,
    "created_at": "2024-01-15T10:30:00",
    "metadata": {}
  }
]
```

**Example:**
```bash
curl http://localhost:8000/api/v1/checkpoints/{checkpoint_id}/files
```

---

#### DELETE /checkpoints/{checkpoint_id}

Delete a checkpoint.

**Parameters:**
- `checkpoint_id` (path) - Checkpoint identifier

**Response:** `204 No Content`

**Errors:**
- `404 Not Found` - Checkpoint not found

**Example:**
```bash
curl -X DELETE http://localhost:8000/api/v1/checkpoints/{checkpoint_id}
```

---

#### GET /checkpoints/sessions/{session_id}/stats

Get checkpoint statistics for a session.

**Parameters:**
- `session_id` (path) - Session identifier

**Response:** `200 OK`
```json
{
  "session_id": "session_123",
  "checkpoint_count": 10,
  "total_files": 45,
  "total_size_bytes": 125000,
  "active_checkpoints": 8,
  "restored_checkpoints": 2
}
```

**Example:**
```bash
curl http://localhost:8000/api/v1/checkpoints/sessions/session_123/stats
```

---

#### POST /checkpoints/cleanup

Clean up expired checkpoints.

**Response:** `200 OK`
```json
{
  "message": "Cleaned up 5 expired checkpoints",
  "count": 5
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/checkpoints/cleanup
```

---

## Data Models

### Checkpoint

```typescript
{
  id: string;              // UUID
  session_id: string;      // Session identifier
  user_message?: string;   // Optional message
  checkpoint_type: "auto" | "manual";
  status: "active" | "restored" | "expired";
  created_at: datetime;    // ISO 8601
  restored_at?: datetime;  // ISO 8601
  expires_at?: datetime;   // ISO 8601
  file_count: number;      // Number of files
  total_size_bytes: number;// Total size in bytes
  metadata?: object;       // Additional metadata
  is_deleted: boolean;     // Soft delete flag
}
```

### FileSnapshot

```typescript
{
  id: string;              // UUID
  checkpoint_id: string;   // Parent checkpoint
  file_path: string;       // Original file path
  content_hash: string;    // SHA-256 hash
  size_bytes: number;      // File size in bytes
  created_at: datetime;    // ISO 8601
  storage_path: string;    // Path in storage
  metadata?: object;       // Additional metadata
}
```

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### HTTP Status Codes

- `200 OK` - Successful request
- `201 Created` - Resource created successfully
- `204 No Content` - Successful deletion
- `400 Bad Request` - Invalid request data
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## Rate Limiting

Currently, no rate limiting is implemented. In production, consider adding rate limiting to prevent abuse.

## Pagination

List endpoints support pagination:

- `limit` - Maximum number of results (default: 100, max: 1000)
- `offset` - Number of results to skip (default: 0)

Example:
```bash
curl "http://localhost:8000/api/v1/checkpoints/sessions/session_123?limit=20&offset=40"
```

## Best Practices

1. **Create checkpoints before major changes** - Always checkpoint before refactoring or making significant edits

2. **Use descriptive messages** - Include meaningful `user_message` values to identify checkpoints later

3. **Clean up regularly** - Run the cleanup endpoint periodically or set up a cron job

4. **Monitor storage** - Use session stats to track storage usage

5. **Limit file paths** - Only include files that actually changed to minimize storage

## SDK Usage

### Python

```python
from src.core.checkpointing import checkpoint_manager

# Set session
checkpoint_manager.set_session("session_123")

# Create checkpoint
checkpoint_id = await checkpoint_manager.auto_checkpoint(
    file_paths=["file1.py", "file2.py"],
    user_message="Before refactoring"
)

# Restore checkpoint
await checkpoint_manager.rewind(checkpoint_id, restore_code=True)

# Get checkpoints
checkpoints = checkpoint_manager.get_session_checkpoints()
```

### cURL Examples

See individual endpoint documentation for cURL examples.
