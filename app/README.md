# Accessibility Reviewer GitHub App

Flask-based GitHub App for automated PR accessibility reviews.

## Structure

```
app/
├── __init__.py              # Package initialization
├── github_app_auth.py       # GitHub App authentication (JWT + installation tokens)
├── guide_loader.py          # Loads accessibility guides
├── pr_reviewer.py           # Core review logic using Scout AI
├── comment_poster.py        # Posts inline PR comments
└── webhook_server.py        # Flask server with webhook endpoint
```

## Key Components

### `github_app_auth.py`
- Generates JWT for GitHub App authentication
- Retrieves installation tokens for accessing repositories
- Handles token caching (1 hour expiration)

### `guide_loader.py`
- Loads accessibility guides from `guides/` directory
- Detects platforms from file extensions
- Combines relevant guides for AI context

### `pr_reviewer.py`
- Core review engine using Scout AI
- Adapted from `scripts/pr-review-ci-scout.py`
- Handles batching, retries, and issue normalization

### `comment_poster.py`
- Posts inline review comments at specific file:line
- Posts commit statuses (success/failure)
- Formats issues with emoji, WCAG info, and suggested fixes

### `webhook_server.py`
- Flask server receiving GitHub webhooks
- Orchestrates the review process
- Health check and status endpoints

## Environment Variables

See [../.env.example](../.env.example) for full list.

**Required:**
- `GITHUB_APP_ID` - Your GitHub App ID
- `GITHUB_APP_PRIVATE_KEY` - Private key (PEM format)
- `GITHUB_WEBHOOK_SECRET` - Webhook signature secret
- `SCOUT_API_KEY` - Scout API key
- `SCOUT_BASE_URL` - Scout API base URL

**Optional:**
- `PORT` - Server port (default: 8080)
- `SCOUT_MODEL` - Model name (default: gpt-5.2)
- `SCOUT_MAX_TOKENS` - Max tokens (default: 2500)
- `SCOUT_TEMPERATURE` - Temperature (default: 0.0)
- `SCOUT_FILES_PER_BATCH` - Files per batch (default: 1)
- `SCOUT_MAX_DIFF_CHARS` - Max diff chars (default: 180000)
- `SCOUT_MAX_SNIPPET_LINES` - Max snippet lines (default: 30)
- `SCOUT_RETRY_ATTEMPTS` - Retry attempts (default: 4)

## Running Locally

```bash
# Install dependencies
pip install -r requirements-app.txt

# Configure environment
cp .env.example .env
# Edit .env with your values

# Run server
python app/webhook_server.py
```

Server starts on http://0.0.0.0:8080

## Endpoints

- `GET /` - Service info
- `GET /health` - Health check
- `POST /webhook` - GitHub webhook endpoint

## Testing

Use ngrok to expose local server:

```bash
ngrok http 8080
```

Update GitHub App webhook URL to ngrok URL.

## Deployment

See [../GITHUB_APP_SETUP.md](../GITHUB_APP_SETUP.md) for deployment instructions.

**Recommended:** Railway or Render for easy deployment.

## Workflow

1. PR opened/updated on installed repo
2. GitHub sends webhook to `/webhook`
3. Server validates signature
4. Server generates installation token
5. Server fetches PR diff and changed files
6. Server loads relevant accessibility guides
7. Server calls Scout AI with diff + guides
8. AI returns accessibility issues
9. Server posts inline review comments
10. Server updates commit status

## Architecture

See [../GITHUB_APP_DESIGN.md](../GITHUB_APP_DESIGN.md) for detailed architecture.
