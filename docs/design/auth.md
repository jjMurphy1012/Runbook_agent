# Auth Strategy

Stateless JWT. Spring Session removed; Redis is reserved for cache and streams only.

- Login/register endpoints issue signed JWT tokens
- All API requests carry `Authorization: Bearer <token>`
- Spring Security configured with `SessionCreationPolicy.STATELESS`
- `spring-session-data-redis` removed from pom.xml
