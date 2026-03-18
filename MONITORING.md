# Monitoring Setup

## Free Monitoring Options

### 1. Uptime Monitoring (Recommended)

Sign up at https://uptimerobot.com (free):

1. Create account
2. Add new monitor:
   - Type: HTTPS
   - URL: Your Render app URL (e.g., `https://omnirom.onrender.com`)
   - Interval: 5 minutes
3. Get alerts via email/Discord/Slack

### 2. Render Dashboard

- Access at: https://dashboard.render.com
- View: Your service → Logs
- Check: Metrics tab for CPU/memory

### 3. API Stats

- Endpoint: `GET /v1/stats`
- Returns: Request count, cache hit rate, language breakdown

## Health Check

- Endpoint: `GET /health`
- Returns: `{"status": "healthy", "cache_enabled": <bool>}`
- Use for: Load balancer health checks, uptime monitoring

## Redis Cache

- Endpoint: `GET /v1/cache/stats` – view cache stats
- Endpoint: `POST /v1/cache/clear` – clear all cached results

## Logs

- View at: Render Dashboard → Your Service → Logs
- Format: Timestamped structured log lines to stdout/stderr

## Free Stack Summary

| Component | Option | Notes |
|-----------|--------|-------|
| Backend hosting | [Render](https://render.com) | 750 hrs/mo free |
| Redis cache | [Aiven Valkey](https://aiven.io) | 30 MB free |
| CI/CD | GitHub Actions | 2000 min/mo |
| Uptime monitoring | UptimeRobot | Free, 5-min checks |
| Container registry | GitHub Container Registry | Unlimited public |
