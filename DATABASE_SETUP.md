# Database Setup for Render PostgreSQL

This document outlines the database configuration requirements for deploying Foe Foundry with Render PostgreSQL.

## Environment Variables

The application requires the following environment variable to connect to PostgreSQL:

```bash
DATABASE_URL=postgresql://username:password@host:port/database_name
```

Render automatically provides this variable when you add a PostgreSQL service to your application.

## PostgreSQL-Specific Configuration

The authentication system is configured with PostgreSQL-optimized settings:

### Connection Pool Configuration
- **Pool Size**: 10 connections maintained
- **Max Overflow**: 20 additional connections when pool is full
- **Pool Timeout**: 30 seconds to get connection from pool
- **Pool Recycle**: Connections recycled after 1 hour
- **Pre-ping**: Connections validated before use

### SSL Configuration
- **SSL Mode**: Required (mandatory for Render PostgreSQL)
- **Connection Timeout**: 10 seconds

### Automatic Table Creation
- Tables are created automatically using SQLModel metadata
- No manual migrations required for initial setup
- Database schema is version-controlled through model definitions

## Database Schema

The authentication system creates the following tables:

### `users` table
- Primary key: `id` (auto-increment integer)
- Unique email index for fast lookups
- Indexed OAuth provider IDs (google_id, patreon_id, discord_id)
- Timezone-aware timestamps (UTC)

### `anon_sessions` table  
- Primary key: `anon_id` (string)
- Tracks anonymous user credit usage
- Timezone-aware timestamps (UTC)

## Health Monitoring

The application provides a database health check endpoint:

```
GET /auth/health
```

Returns:
- `200 OK` with `{"status": "healthy", "database": "connected"}` if database is accessible
- `503 Service Unavailable` if database connection fails

## Error Handling

The database configuration includes:
- Automatic connection retry via pool pre-ping
- Graceful session cleanup on errors
- Detailed logging of database connection issues
- Fallback error messages without exposing sensitive connection details

## Performance Considerations

### Connection Management
- Connection pooling prevents excessive database connections
- Automatic connection recycling prevents stale connections
- Pool overflow handles traffic spikes gracefully

### Query Optimization
- Proper indexing on frequently queried fields (email, OAuth IDs)
- Timezone-aware datetime handling prevents conversion issues
- Efficient session management with minimal database queries

## Migration Strategy

For future schema changes:
- Consider implementing Alembic for formal migrations
- Current auto-creation works for initial deployment
- Monitor for breaking changes requiring data migration

## Troubleshooting

### Common Issues

1. **Connection Timeouts**
   - Check Render PostgreSQL service status
   - Verify DATABASE_URL environment variable
   - Check network connectivity

2. **SSL Certificate Issues**
   - Ensure `sslmode=require` in connection string
   - Render PostgreSQL requires SSL connections

3. **Pool Exhaustion**
   - Monitor connection pool usage
   - Adjust pool_size and max_overflow if needed
   - Check for connection leaks in application code

### Debug Commands

```bash
# Test database connectivity
curl http://your-app.onrender.com/auth/health

# Check application logs
render logs --service your-service-name
```

## Environment-Specific Notes

### Development (SQLite)
- Falls back to SQLite when DATABASE_URL not set
- Uses `foe_foundry_accounts.db` file
- Simplified connection settings

### Production (Render PostgreSQL)  
- Uses connection pooling and SSL
- Optimized for concurrent access
- Health monitoring enabled

The configuration automatically detects the database type and applies appropriate settings.