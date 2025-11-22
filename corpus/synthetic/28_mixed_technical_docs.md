API Integration Guide
# Authentication
The API supports two authentication methods:
- API Key - Include key in X-API-Key header
- OAuth 2.0 - Use bearer token authentication
# Endpoint Reference
| Endpoint | Method | Description |
| --- | --- | --- |
| /api/users | GET | List all users |
| /api/users/{id} | GET | Get user by ID |
| /api/users | POST | Create new user |
# Rate Limits
- Standard Tier: 1,000 requests/hour
- Premium Tier: 10,000 requests/hour
- Enterprise: Custom limits