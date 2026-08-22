# Auth service (V1)

Layered FastAPI auth: **route → controller → service → database**.

```
services/auth/
├── routes/auth_routes.py
├── controller/auth_controller.py
├── services/auth_service.py
├── services/auth_health.py
├── schema/auth_schema.py
└── middleware/auth_middleware.py
```

User rows live in `infrastructure/database/models/user.py`, not in this package.

## Endpoints

| Method | Path | Auth |
|---|---|---|
| GET | `/api/v1/auth/health` | no |
| POST | `/api/v1/auth/register` | no |
| POST | `/api/v1/auth/login` | no |
| GET | `/api/v1/auth/me` | Bearer JWT |
| PATCH | `/api/v1/auth/me` | Bearer JWT |
| PUT | `/api/v1/auth/me` | Bearer JWT |

Passwords are hashed with bcrypt. Soft-deleted users (`deleted_at` set) cannot log in or use `/api/v1/auth/me`. Identity only (`name`, `email`). Profile and goals live on `/api/v1/users/me`.
