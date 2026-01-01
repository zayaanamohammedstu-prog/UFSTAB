# OratorHub API Documentation

## Base URL
```
Development: http://localhost:5000/api
Production: https://yourdomain.com/api
```

## Authentication

All protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

### Register
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "password": "password123",
  "full_name": "Full Name",
  "institution": "University Name",
  "role": "user"  // user, judge, organizer, admin
}

Response (201):
{
  "message": "User registered successfully",
  "user": {...},
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}

Response (200):
{
  "message": "Login successful",
  "user": {...},
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Get Current User
```http
GET /auth/me
Authorization: Bearer <token>

Response (200):
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "full_name": "Full Name",
  "role": "user",
  "institution": "University",
  "created_at": "2026-01-01T00:00:00",
  "is_active": true
}
```

## Tournaments

### List All Tournaments
```http
GET /tournaments

Response (200):
[
  {
    "id": 1,
    "name": "World Championships",
    "format": "BP",
    "start_date": "2026-02-15T00:00:00",
    "end_date": "2026-02-20T00:00:00",
    "venue": "Cambridge University",
    "num_rounds": 9,
    "registration_fee": 100.0,
    "max_participants": 400,
    "event_type": "hybrid",
    "status": "upcoming"
  }
]
```

### Get Tournament
```http
GET /tournaments/:id

Response (200):
{
  "id": 1,
  "name": "World Championships",
  ...
}
```

### Create Tournament
```http
POST /tournaments
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Tournament Name",
  "description": "Tournament description",
  "format": "BP",  // BP, APDA, WSDC
  "start_date": "2026-02-15T00:00:00Z",
  "end_date": "2026-02-20T00:00:00Z",
  "venue": "Venue Name",
  "num_rounds": 5,
  "registration_fee": 50.0,
  "max_participants": 200,
  "registration_deadline": "2026-02-01T00:00:00Z",
  "event_type": "in-person"  // in-person, virtual, hybrid
}

Response (201):
{
  "message": "Tournament created successfully",
  "tournament": {...}
}
```

### Update Tournament
```http
PUT /tournaments/:id
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Updated Name",
  "status": "ongoing"
}

Response (200):
{
  "message": "Tournament updated successfully",
  "tournament": {...}
}
```

### Delete Tournament
```http
DELETE /tournaments/:id
Authorization: Bearer <token>

Response (200):
{
  "message": "Tournament deleted successfully"
}
```

### Get Tournament Standings
```http
GET /tournaments/:id/standings

Response (200):
[
  {
    "rank": 1,
    "id": 1,
    "name": "Team Name",
    "institution": "University",
    "points": 15,
    "wins": 5,
    "speaker_points": 720.5
  }
]
```

## Registrations

### Register for Tournament
```http
POST /registrations
Authorization: Bearer <token>
Content-Type: application/json

{
  "tournament_id": 1,
  "registration_type": "team",  // individual, team
  "team_name": "Team Name",
  "partner_name": "Partner Name",
  "partner_email": "partner@example.com"
}

Response (201):
{
  "message": "Registration created successfully",
  "registration": {
    "id": 1,
    "status": "pending",  // pending, confirmed, waitlist, cancelled
    "payment_status": "pending"
  }
}
```

### Upload Document
```http
POST /registrations/:id/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <file>

Response (200):
{
  "message": "Document uploaded successfully",
  "filename": "user_123_case.pdf"
}
```

### Process Payment
```http
POST /registrations/:id/payment
Authorization: Bearer <token>
Content-Type: application/json

{
  "payment_id": "stripe_payment_id"
}

Response (200):
{
  "message": "Payment processed successfully",
  "registration": {
    "payment_status": "completed",
    "status": "confirmed"
  }
}
```

### Get My Registrations
```http
GET /registrations/my-registrations
Authorization: Bearer <token>

Response (200):
[
  {
    "id": 1,
    "tournament_id": 1,
    "status": "confirmed",
    ...
  }
]
```

## Teams

### Create Team
```http
POST /teams
Authorization: Bearer <token>
Content-Type: application/json

{
  "tournament_id": 1,
  "name": "Team Name",
  "institution": "University",
  "speaker1_name": "Speaker One",
  "speaker2_name": "Speaker Two"
}

Response (201):
{
  "message": "Team created successfully",
  "team": {...}
}
```

### Get Team
```http
GET /teams/:id

Response (200):
{
  "id": 1,
  "name": "Team Name",
  "institution": "University",
  "speaker1_name": "Speaker One",
  "speaker2_name": "Speaker Two",
  "points": 0,
  "wins": 0,
  "speaker_points": 0.0
}
```

## Rounds & Pairings

### Create Round
```http
POST /rounds
Authorization: Bearer <token>
Content-Type: application/json

{
  "tournament_id": 1,
  "round_number": 1,
  "motion": "This House supports...",
  "info_slide": "Context information",
  "motion_release_time": "2026-02-15T10:00:00Z"
}

Response (201):
{
  "message": "Round created successfully",
  "round": {...}
}
```

### Generate Draw
```http
POST /rounds/:id/generate-draw
Authorization: Bearer <token>

Response (200):
{
  "message": "Draw generated successfully",
  "pairings": [...]
}
```

### Get Round Pairings
```http
GET /rounds/:id/pairings

Response (200):
{
  "round": {...},
  "pairings": {
    "Room 1": [
      {
        "team": {...},
        "position": "OG",
        "judges": [...]
      },
      ...
    ]
  }
}
```

## Scores

### Submit Score
```http
POST /scores
Authorization: Bearer <token>
Content-Type: application/json

{
  "pairing_id": 1,
  "speaker_name": "Speaker Name",
  "score": 75.5,
  "feedback": "Excellent arguments",
  "rank": 1
}

Response (201):
{
  "message": "Score created successfully",
  "score": {...}
}
```

### Get Pairing Scores
```http
GET /scores/pairing/:id

Response (200):
[
  {
    "id": 1,
    "speaker_name": "Speaker One",
    "score": 75.5,
    "feedback": "Great speech",
    "rank": 1
  }
]
```

## Real-Time Events

### Event Stream (SSE)
```http
GET /stream/events

Response (text/event-stream):
data: {"type":"pairing_update","data":{...},"timestamp":1234567890}

data: {"type":"result_update","data":{...},"timestamp":1234567891}
```

Event Types:
- `heartbeat` - Connection keepalive
- `tournament_created` - New tournament
- `pairing_update` - Pairings updated
- `result_update` - Results updated
- `motion_released` - Motion released
- `registration_confirmed` - Registration confirmed

## Error Responses

All errors follow this format:
```json
{
  "error": "Error message description"
}
```

Status Codes:
- `400` - Bad Request (missing/invalid data)
- `401` - Unauthorized (not logged in)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `500` - Internal Server Error

## Rate Limiting

- 100 requests per minute per IP
- 1000 requests per hour per user

Exceeded limits return `429 Too Many Requests`.

## Pagination

List endpoints support pagination:
```http
GET /tournaments?page=1&per_page=20
```

Default: `per_page=30`, max: `per_page=100`

## Filtering & Sorting

Some endpoints support filtering:
```http
GET /tournaments?status=upcoming&format=BP
GET /tournaments?sort=start_date&order=desc
```

## Health Check

```http
GET /health

Response (200):
{
  "status": "healthy",
  "service": "OratorHub API",
  "version": "1.0.0"
}
```
