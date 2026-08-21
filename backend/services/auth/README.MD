# Auth service (V1)

Layered FastAPI auth: **route → controller → service → database**.

```
services/auth/
├── routes/auth_routes.py
├── controller/auth_controller.py
├── services/auth_service.py
├── services/auth_health.py
├── schema/auth.py
└── middleware/deps.py
```

User rows live in `infrastructure/database/models/user.py`, not in this package.

## Endpoints

| Method | Path | Auth |
|---|---|---|
| GET | `/auth/health` | no |
| POST | `/auth/register` | no |
| POST | `/auth/login` | no |
| GET | `/auth/me` | Bearer JWT |
| PATCH | `/auth/me` | Bearer JWT |
| PUT | `/auth/me` | Bearer JWT |

Passwords are hashed with bcrypt. Soft-deleted users (`deleted_at` set) cannot log in or use `/auth/me`.
