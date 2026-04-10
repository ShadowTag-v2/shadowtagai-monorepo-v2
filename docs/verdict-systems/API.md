# Verdict Systems API Reference

## Base URL

```
http://localhost:8001   (Development)
https://api.verdict.systems   (Production)
```

## Authentication

_(To be implemented - OAuth2 / JWT)_

```http
Authorization: Bearer YOUR_TOKEN
```

---

## Core Endpoints

### Health Check

```http
GET /health
```

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2025-11-17T12:00:00Z",
  "engine": "Schiznit v1.0",
  "active_users": 150,
  "active_tasks": 3420,
  "active_lockouts": 12
}
```

---

## Task Management

### Create Task

```http
POST /tasks
Content-Type: application/json
```

**Request Body:**

```json
{
  "title": "Complete homework assignment",
  "description": "Math chapter 5 problems",
  "deadline": "2025-11-18T14:00:00Z",
  "estimated_duration_minutes": 45,
  "priority": 4,
  "user_id": "student_001",
  "vertical": "school",
  "enable_lockout": true,
  "blocked_apps": ["instagram", "tiktok"],
  "ai_tutor_enabled": true
}
```

**Response:** `201 Created`

```json
{
  "id": "task_20251117_abc123",
  "title": "Complete homework assignment",
  "urgency_level": "yellow",
  "status": "pending",
  ...
}
```

---

### Get User Tasks

```http
GET /tasks?user_id=student_001&status=pending&urgency=red
```

**Query Parameters:**

- `user_id` (required): User ID
- `status` (optional): Filter by status
- `urgency` (optional): Filter by urgency level
- `vertical` (optional): Filter by vertical

**Response:** `200 OK`

```json
[
  {
    "id": "task_001",
    "title": "Submit essay",
    "urgency_level": "red",
    "time_remaining": "2:30:00",
    ...
  }
]
```

---

### Complete Task

```http
POST /tasks/{task_id}/complete
Content-Type: application/json
```

**Request Body:**

```json
{
  "completion_method": "manual",
  "completed_by": "student_001",
  "notes": "Finished all problems",
  "submission_url": "https://..."
}
```

**Response:** `200 OK`

---

## Dashboard

### Get User Dashboard

```http
GET /dashboard/{user_id}
```

**Response:** `200 OK`

```json
{
  "user_id": "student_001",
  "urgency_summary": {
    "green": 5,
    "yellow": 3,
    "red": 1,
    "critical": 0
  },
  "next_deadlines": [...],
  "lockout_status": {...},
  "completed_today": 4
}
```

---

### Get Urgency Tiles

```http
GET /urgency-tiles/{user_id}
```

**Response:** `200 OK`

```json
{
  "green": [
    {"id": "task_001", "title": "Read chapter 6", ...}
  ],
  "yellow": [...],
  "red": [...],
  "critical": [...]
}
```

---

## Lockout Management

### Get Lockout Status

```http
GET /lockout/{user_id}/{device_id}
```

**Response:** `200 OK`

```json
{
  "lockout_active": true,
  "lockout_mode": "strict",
  "blocked_apps": ["instagram", "tiktok", "youtube"],
  "locked_tasks": [
    {
      "id": "task_001",
      "title": "Math homework",
      "deadline": "2025-11-17T14:00:00Z",
      "urgency": "critical"
    }
  ]
}
```

---

### Override Lockout

```http
POST /lockout/{user_id}/override?admin_id=parent_001&reason=Emergency&duration_minutes=30
```

**Response:** `200 OK`

```json
{
  "override_active": true,
  "admin_id": "parent_001",
  "reason": "Emergency",
  "duration_minutes": 30,
  "expires_at": "2025-11-17T13:30:00Z"
}
```

---

## School Vertical

### Create Assignment

```http
POST /school/assignments
Content-Type: application/json
```

**Request Body:**

```json
{
  "title": "Chapter 5 Homework",
  "description": "Complete problems 1-20",
  "deadline": "2025-11-18T14:00:00Z",
  "user_id": "student_001",
  "subject": "Algebra II",
  "teacher_id": "teacher_jones",
  "assignment_type": "homework",
  "submission_required": true,
  "ai_tutor_enabled": true,
  "enable_lockout": true
}
```

**Response:** `201 Created`

---

### Submit Assignment

```http
POST /school/assignments/{task_id}/submit?student_id=student_001&submission_url=https://...
```

**Response:** `200 OK`

---

### Grade Assignment

```http
POST /school/assignments/{task_id}/grade
Content-Type: application/json
```

**Request Body:**

```json
{
  "task_id": "task_001",
  "student_id": "student_001",
  "teacher_id": "teacher_jones",
  "grade": "A",
  "score": 95.0,
  "feedback": "Excellent work!",
  "approved": true
}
```

**Response:** `200 OK`

---

### Start AI Tutor

```http
POST /school/ai-tutor/start?task_id=task_001&student_id=student_001&subject=Algebra
```

**Response:** `200 OK`

```json
{
  "session_id": "tutor_20251117_xyz",
  "task_id": "task_001",
  "student_id": "student_001",
  "subject": "Algebra",
  "max_hints": 5,
  "messages": []
}
```

---

## Family Vertical

### Create Family Task

```http
POST /family/tasks
Content-Type: application/json
```

**Request Body:**

```json
{
  "title": "Clean your room",
  "user_id": "child_001",
  "parent_id": "parent_001",
  "task_category": "chore",
  "allowance_value": 5.0,
  "requires_photo_proof": true,
  "deadline": "2025-11-17T18:00:00Z"
}
```

**Response:** `201 Created`

---

## Workplace Vertical

### Create Work Task

```http
POST /workplace/tasks
Content-Type: application/json
```

**Request Body:**

```json
{
  "title": "Complete project proposal",
  "user_id": "employee_001",
  "project_id": "proj_123",
  "manager_id": "manager_001",
  "billable": true,
  "estimated_hours": 4.0,
  "focus_mode": "strict",
  "deadline": "2025-11-20T17:00:00Z"
}
```

**Response:** `201 Created`

---

### Start Focus Session

```http
POST /workplace/focus-session/start?user_id=employee_001&task_id=task_001&duration_minutes=90
```

**Response:** `200 OK`

```json
{
  "session_id": "focus_20251117_abc",
  "user_id": "employee_001",
  "task_id": "task_001",
  "duration_minutes": 90,
  "started_at": "2025-11-17T10:00:00Z"
}
```

---

## Medical Vertical

### Create Medical Task

```http
POST /medical/tasks
Content-Type: application/json
```

**Request Body:**

```json
{
  "title": "Take morning medication",
  "user_id": "senior_001",
  "task_category": "medication",
  "recurring": true,
  "recurrence_pattern": "daily",
  "requires_photo_proof": true,
  "critical_health_task": true,
  "caregiver_id": "caregiver_001",
  "deadline": "2025-11-17T08:00:00Z"
}
```

**Response:** `201 Created`

---

### Record Medication Taken

```http
POST /medical/medication/taken
Content-Type: application/json
```

**Request Body:**

```json
{
  "reminder_id": "med_001",
  "user_id": "senior_001",
  "medication_name": "Metformin",
  "dosage": "500mg",
  "scheduled_time": "08:00",
  "taken_at": "2025-11-17T08:05:00Z",
  "photo_proof_url": "https://...",
  "caregiver_confirmed": true
}
```

**Response:** `200 OK`

---

### Trigger Safety Alert

```http
POST /medical/safety-alert
Content-Type: application/json
```

**Request Body:**

```json
{
  "alert_id": "alert_001",
  "user_id": "senior_001",
  "alert_type": "fall",
  "triggered_at": "2025-11-17T15:30:00Z",
  "location": "Living Room",
  "emergency_services_notified": false
}
```

**Response:** `200 OK`

---

## WebSocket Events _(Future)_

### Task Urgency Updates

```javascript
const ws = new WebSocket("ws://localhost:8001/ws/tasks/student_001");

ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  console.log("Task urgency updated:", update);
};
```

**Event Format:**

```json
{
  "type": "urgency_change",
  "task_id": "task_001",
  "old_urgency": "yellow",
  "new_urgency": "red",
  "time_remaining": "1:30:00"
}
```

---

## Error Responses

### 400 Bad Request

```json
{
  "error": "Validation error",
  "detail": "deadline must be in the future"
}
```

### 404 Not Found

```json
{
  "error": "Task not found",
  "detail": "Task task_001 does not exist"
}
```

### 500 Internal Server Error

```json
{
  "error": "Internal server error",
  "detail": "Database connection failed",
  "timestamp": "2025-11-17T12:00:00Z"
}
```

---

## Rate Limits

- **Free Tier**: 100 requests/minute
- **Plus**: 1,000 requests/minute
- **Family/Business**: 10,000 requests/minute
- **Enterprise**: Unlimited

---

## SDK Examples

### Python

```python
import requests

# Create task
response = requests.post(
    "http://localhost:8001/tasks",
    json={
        "title": "Complete homework",
        "deadline": "2025-11-18T14:00:00Z",
        "user_id": "student_001",
        "vertical": "school"
    }
)
task = response.json()
```

### JavaScript

```javascript
// Get dashboard
const response = await fetch("http://localhost:8001/dashboard/student_001");
const dashboard = await response.json();
console.log(`Urgency summary:`, dashboard.urgency_summary);
```

---

## Support

- **API Issues**: api@verdict.systems
- **Documentation**: https://docs.verdict.systems/api
- **Status**: https://status.verdict.systems/api
