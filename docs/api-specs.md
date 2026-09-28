# API Specification — AI Job Copilot (Phase 1)

Base URL: `http://localhost:8000`  
Swagger UI: `http://localhost:8000/docs`  
ReDoc: `http://localhost:8000/redoc`

---

## 1. System Health

### GET `/health`
Root health check probe for load balancers and container orchestrators.

**Response `200 OK`**:
```json
{
  "status": "healthy"
}
```

### GET `/api/v1/health`
Detailed diagnostics probe reporting database status and latency.

**Response `200 OK`**:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "environment": "development",
  "timestamp": "2026-09-27T10:00:00.000Z",
  "database": {
    "connected": true,
    "latency_ms": 2.45,
    "status": "healthy"
  }
}
```

---

## 2. Users (`/api/v1/users`)

### GET `/api/v1/users`
Retrieve paginated list of users.
* Query parameters: `page` (default 1), `page_size` (default 10)

**Response `200 OK`**:
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "a0000000-0000-0000-0000-000000000001",
        "name": "Alex Chen",
        "email": "alex.chen@example.com",
        "created_at": "2026-09-27T10:00:00.000Z",
        "updated_at": "2026-09-27T10:00:00.000Z"
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 10,
      "total_items": 1,
      "total_pages": 1,
      "has_next": false,
      "has_prev": false
    }
  },
  "message": "Users retrieved successfully",
  "timestamp": "2026-09-27T10:00:00.000Z"
}
```

### POST `/api/v1/users`
Create a new user identity.

**Request Body**:
```json
{
  "name": "Jane Doe",
  "email": "jane.doe@example.com"
}
```

---

## 3. Profiles (`/api/v1/profiles`)

### GET `/api/v1/profiles/{user_id}`
Retrieve candidate job search profile.

**Response `200 OK`**:
```json
{
  "success": true,
  "data": {
    "id": "b0000000-0000-0000-0000-000000000001",
    "user_id": "a0000000-0000-0000-0000-000000000001",
    "preferred_roles": ["Staff Software Engineer", "Full Stack Architect"],
    "preferred_locations": ["Remote", "San Francisco, CA"],
    "years_of_experience": 8,
    "resume_url": "https://storage.jobcopilot.dev/resumes/sample.pdf",
    "created_at": "2026-09-27T10:00:00.000Z",
    "updated_at": "2026-09-27T10:00:00.000Z"
  }
}
```

### PUT `/api/v1/profiles/{user_id}`
Upsert candidate job search preferences.

---

---

## 4. Resume Management (`/api/v1/resume`)

All resume endpoints authenticate the candidate using session or the `X-User-Id` header (defaulting to the demo user `a0000000-0000-0000-0000-000000000001` in local development). Internal storage filepaths are **never** exposed in any response.

### POST `/api/v1/resume/upload`
Upload a new resume or replace an existing resume.
* **Content-Type**: `multipart/form-data`
* **Form Field**: `file` (Binary document)
* **Allowed MIME Types**: `application/pdf`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
* **Allowed Extensions**: `.pdf`, `.docx`
* **Maximum Size**: 10 MB (10,485,760 bytes)
* **Deep Binary Inspection**: Magic number check (`%PDF-`, `PK\x03\x04` with OpenXML document structure), executable signatures (`MZ`, `\x7fELF`, etc.) and image formats (`\x89PNG`, `\xff\xd8\xff`) are rejected.
* **Behavior**: If a resume already exists for the user, it automatically deletes the previous file on disk and updates the record in-place.

**Response `201 Created`**:
```json
{
  "success": true,
  "data": {
    "id": "e0000000-0000-0000-0000-000000000001",
    "userId": "a0000000-0000-0000-0000-000000000001",
    "originalFilename": "Alex_Chen_Staff_Engineer_Resume.pdf",
    "fileType": "application/pdf",
    "fileSize": 184520,
    "uploadedAt": "2026-09-27T10:00:00.000Z",
    "updatedAt": "2026-09-27T10:00:00.000Z",
    "downloadUrl": "/api/v1/resume/download"
  },
  "message": "Resume uploaded and verified successfully.",
  "timestamp": "2026-09-27T10:00:00.000Z"
}
```

### GET `/api/v1/resume`
Retrieve metadata for the current user's active resume.

**Response `200 OK`**:
```json
{
  "success": true,
  "data": {
    "id": "e0000000-0000-0000-0000-000000000001",
    "userId": "a0000000-0000-0000-0000-000000000001",
    "originalFilename": "Alex_Chen_Staff_Engineer_Resume.pdf",
    "fileType": "application/pdf",
    "fileSize": 184520,
    "uploadedAt": "2026-09-27T10:00:00.000Z",
    "updatedAt": "2026-09-27T10:00:00.000Z",
    "downloadUrl": "/api/v1/resume/download"
  },
  "message": "Resume metadata retrieved successfully.",
  "timestamp": "2026-09-27T10:00:00.000Z"
}
```

**Response `404 Not Found`**:
When no resume exists for the user.

### GET `/api/v1/resume/download`
Download the original resume document stream.

**Response `200 OK`**:
* **Content-Type**: `application/pdf` or `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
* **Content-Disposition**: `attachment; filename="Alex_Chen_Staff_Engineer_Resume.pdf"`
* **Body**: Raw binary document bytes.

### DELETE `/api/v1/resume`
Permanently remove the active resume file from storage and delete the database record.

**Response `200 OK`**:
```json
{
  "success": true,
  "data": {
    "success": true,
    "message": "Resume successfully deleted."
  },
  "message": "Resume deleted successfully.",
  "timestamp": "2026-09-27T10:00:00.000Z"
}
```

---

## 5. Error Standards

Every non-2xx response returns a standard error envelope:
```json
{
  "success": false,
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "User with identifier '...' was not found.",
    "details": {}
  },
  "timestamp": "2026-09-27T10:00:00.000Z",
  "correlation_id": "d8e3b4a2-7b2a-4282-9907-55df988d5e1a"
}
```
