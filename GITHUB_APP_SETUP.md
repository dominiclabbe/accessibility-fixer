# GitHub App Setup Guide

Complete guide to setting up the Accessibility Reviewer GitHub App.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Local Development Setup](#local-development-setup)
4. [GitHub App Registration](#github-app-registration)
5. [Deployment](#deployment)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)

## Overview

The Accessibility Reviewer GitHub App automatically reviews PRs for accessibility issues using AI (Scout) and comprehensive WCAG 2.2 guidelines.

**Key Features:**
- Install once, works on multiple repositories
- Automatic reviews on PR open/update
- Inline comments at specific file:line locations
- Blocks merge on critical issues
- Support for iOS, Android, Web, Flutter

## Prerequisites

- Python 3.11+
- pip
- ngrok (for local testing)
- GitHub account with admin access to create GitHub Apps
- Scout API key from Mirego

## Local Development Setup

### 1. Clone Repository

```bash
cd /Users/dominiclabbe/dev/accessibility-fixer
```

### 2. Install Dependencies

```bash
pip install -r requirements-app.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` and fill in (we'll get these values in next steps):

```bash
# Leave these empty for now - we'll fill them after GitHub App registration
GITHUB_APP_ID=
GITHUB_APP_PRIVATE_KEY=
GITHUB_WEBHOOK_SECRET=

# Scout configuration
SCOUT_API_KEY=your-scout-api-key
SCOUT_BASE_URL=https://interne.scout.mirego.com/api/chat/openai_compatible
SCOUT_MODEL=gpt-5.2

# Server
PORT=8080
```

### 4. Test Server Locally

```bash
python app/webhook_server.py
```

You should see:

```
Starting Accessibility Reviewer GitHub App
Port: 8080
Webhook secret configured: False
GitHub auth configured: False
PR reviewer configured: True
 * Running on http://0.0.0.0:8080
```

Visit http://localhost:8080/health to check status.

### 5. Expose with ngrok

In another terminal:

```bash
ngrok http 8080
```

Note the HTTPS URL (e.g., `https://abc123.ngrok.io`). You'll use this as the webhook URL.

## GitHub App Registration

### 1. Create GitHub App

Go to:
- **Personal account**: https://github.com/settings/apps/new
- **Organization**: https://github.com/organizations/{org}/settings/apps/new

### 2. Fill in App Details

**Basic Information:**
- **GitHub App name**: `Accessibility Reviewer` (must be unique across GitHub)
- **Homepage URL**: `https://github.com/dominiclabbe/accessibility-fixer`
- **Webhook URL**: `https://your-ngrok-url.ngrok.io/webhook` (or deployment URL later)
- **Webhook secret**: Generate a random string (save this!)
  ```bash
  python -c "import secrets; print(secrets.token_hex(32))"
  ```

**Permissions:**

Under "Repository permissions":
- **Pull requests**: Read & Write ✅
- **Contents**: Read ✅
- **Metadata**: Read ✅ (automatically selected)
- **Commit statuses**: Read & Write ✅

**Subscribe to events:**
- ☑️ Pull request

**Where can this GitHub App be installed?**
- Select "Any account" (to allow installation on multiple orgs/repos)

### 3. Create the App

Click "Create GitHub App"

### 4. Generate Private Key

After creation:
1. Scroll down to "Private keys"
2. Click "Generate a private key"
3. A `.pem` file will download
4. Open the file and copy the entire contents

### 5. Note App ID

At the top of the page, note your "App ID" (e.g., `123456`)

### 6. Update Environment Variables

Update your `.env` file:

```bash
GITHUB_APP_ID=123456
GITHUB_APP_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA...
...your full key here...
-----END RSA PRIVATE KEY-----"
GITHUB_WEBHOOK_SECRET=your-webhook-secret-here

SCOUT_API_KEY=your-scout-api-key
SCOUT_BASE_URL=https://interne.scout.mirego.com/api/chat/openai_compatible
SCOUT_MODEL=gpt-5.2
PORT=8080
```

**Important:** The private key must include newlines. In `.env` file, use actual newlines (not `\n`).

### 7. Restart Server

```bash
# Stop the running server (Ctrl+C)
python app/webhook_server.py
```

Now you should see:

```
Webhook secret configured: True
GitHub auth configured: True
PR reviewer configured: True
```

## Testing Locally

### 1. Install App on Test Repository

1. Go to your app settings: https://github.com/settings/apps/{your-app-name}
2. Click "Install App" in left sidebar
3. Select your test repository (e.g., `multiplatform_test_app`)
4. Click "Install"

### 2. Create Test PR

```bash
cd /Users/dominiclabbe/dev/multiplatform_test_app

# Create test branch
git checkout -b test/github-app-review

# Add file with accessibility issue
cat > androidApp/src/main/java/TestButton.kt << 'EOF'
import androidx.compose.material.IconButton
import androidx.compose.material.Icon
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Star

@Composable
fun TestButton() {
    IconButton(onClick = { }) {
        Icon(Icons.Default.Star, contentDescription = null)
    }
}
EOF

# Commit and push
git add .
git commit -m "Test: Button without accessibility label"
git push origin test/github-app-review

# Create PR
gh pr create --title "Test GitHub App review" --body "Testing automated review with GitHub App"
```

### 3. Watch Logs

In your server terminal, you should see:

```
Received webhook: pull_request
Processing PR #X: Test GitHub App review
Changed files: 1
Detected platforms: ['Android']
Loading accessibility guides...
Starting accessibility review...
Found 1 accessibility issues
Posting review comments...
✅ Review complete
```

### 4. Check PR

Go to the PR on GitHub. You should see:
- Inline comment on the file with the issue
- Commit status showing "Accessibility review completed"
- Review comment with summary

## Deployment

### Option 1: Railway (Recommended)

**1. Create Railway Account**
- Go to https://railway.app/
- Sign up with GitHub

**2. Create New Project**
- Click "New Project"
- Select "Deploy from GitHub repo"
- Select `dominiclabbe/accessibility-fixer`
- Railway will auto-detect Python and deploy

**3. Configure Environment Variables**

In Railway dashboard:
- Go to Variables tab
- Add all variables from your `.env` file:
  - `GITHUB_APP_ID`
  - `GITHUB_APP_PRIVATE_KEY` (paste the entire key including BEGIN/END lines)
  - `GITHUB_WEBHOOK_SECRET`
  - `SCOUT_API_KEY`
  - `SCOUT_BASE_URL`
  - `SCOUT_MODEL`
  - `PORT` (Railway will auto-set this, but you can override)

**4. Deploy**

Railway will automatically deploy. Note the deployment URL (e.g., `https://your-app.railway.app`).

**5. Update GitHub App Webhook URL**

1. Go to GitHub App settings
2. Update "Webhook URL" to: `https://your-app.railway.app/webhook`
3. Save changes

**6. Test**

Create a new PR in an installed repo. The app should now receive webhooks at the Railway URL.

### Option 2: Render

**1. Create Render Account**
- Go to https://render.com/
- Sign up with GitHub

**2. Create New Web Service**
- Click "New" → "Web Service"
- Connect your GitHub repo
- Configure:
  - **Name**: `accessibility-reviewer`
  - **Environment**: `Python 3`
  - **Build Command**: `pip install -r requirements-app.txt`
  - **Start Command**: `gunicorn app.webhook_server:app --bind 0.0.0.0:$PORT --workers 2 --timeout 300`

**3. Add Environment Variables**

In Render dashboard, add all variables from `.env`.

**4. Deploy**

Render will deploy and provide a URL.

**5. Update GitHub App**

Update webhook URL in GitHub App settings.

### Option 3: Fly.io

```bash
# Install flyctl
brew install flyctl

# Login
flyctl auth login

# Launch app
cd /Users/dominiclabbe/dev/accessibility-fixer
flyctl launch

# Set secrets
flyctl secrets set GITHUB_APP_ID=123456
flyctl secrets set GITHUB_APP_PRIVATE_KEY="$(cat your-key.pem)"
flyctl secrets set GITHUB_WEBHOOK_SECRET=your-secret
flyctl secrets set SCOUT_API_KEY=your-key
flyctl secrets set SCOUT_BASE_URL=https://interne.scout.mirego.com/api/chat/openai_compatible
flyctl secrets set SCOUT_MODEL=gpt-5.2

# Deploy
flyctl deploy
```

## Installing on Multiple Repositories

Once deployed, you can install the app on any repository:

1. Go to: https://github.com/apps/{your-app-name}
2. Click "Install"
3. Select repositories
4. App will automatically review PRs on those repos

## Configuration

### Tuning Scout Parameters

You can tune the AI behavior with environment variables:

```bash
# Max tokens per request (higher = more detailed responses)
SCOUT_MAX_TOKENS=2500

# Temperature (0 = deterministic, 1 = creative)
SCOUT_TEMPERATURE=0.0

# Files per batch (1 = per-file review, higher = batch multiple files)
SCOUT_FILES_PER_BATCH=1

# Max diff characters per request (prevent timeouts)
SCOUT_MAX_DIFF_CHARS=180000

# Max lines in code snippets (prevent bloat)
SCOUT_MAX_SNIPPET_LINES=30

# Retry attempts for transient errors
SCOUT_RETRY_ATTEMPTS=4
```

### Blocking Merge on Critical Issues

The app automatically:
- Posts review with `REQUEST_CHANGES` if critical issues found
- Sets commit status to `failure` if critical issues found
- This blocks merge if branch protection requires status checks

To enable branch protection:
1. Go to repo Settings → Branches
2. Add protection rule for `main`
3. Enable "Require status checks to pass before merging"
4. Select "accessibility-review"

## Troubleshooting

### Webhook Not Receiving Events

**Check:**
1. Webhook URL is correct in GitHub App settings
2. Server is running and accessible
3. ngrok is running (for local testing)
4. Check webhook deliveries in GitHub App settings

### "Invalid signature" Error

**Solution:**
- Ensure `GITHUB_WEBHOOK_SECRET` matches the secret in GitHub App settings
- Verify `.env` file is loaded correctly

### "GitHub auth not configured"

**Solution:**
- Verify `GITHUB_APP_ID` is set correctly
- Verify `GITHUB_APP_PRIVATE_KEY` includes full key with BEGIN/END lines
- Check for syntax errors in `.env` file

### Scout API Errors

**Check:**
1. `SCOUT_API_KEY` is valid
2. `SCOUT_BASE_URL` is correct (no trailing `/v1`)
3. `SCOUT_MODEL` name is correct
4. Network connectivity to Scout endpoint

### No Comments Posted

**Check:**
1. App has "Pull requests: Read & Write" permission
2. Installation token is valid (check logs)
3. PR has changed files that match supported extensions
4. No errors in server logs

### Diff Too Large

**Solution:**
- Increase `SCOUT_MAX_DIFF_CHARS`
- Or decrease `SCOUT_FILES_PER_BATCH` to 1 (per-file review)

## Cost Estimation

Using Scout (gpt-5.2):

| PR Size | Est. Cost per Review |
|---------|---------------------|
| Small (< 10 files) | ~$0.05-0.10 |
| Medium (10-50 files) | ~$0.10-0.30 |
| Large (50+ files) | ~$0.30-0.50 |

**Monthly estimate:** ~$5-25 for typical team (50-100 PRs/month)

## Monitoring

### Health Check

```bash
curl https://your-app.railway.app/health
```

Expected response:

```json
{
  "status": "healthy",
  "checks": {
    "webhook_secret": true,
    "github_auth": true,
    "pr_reviewer": true
  }
}
```

### Logs

**Railway:**
- View logs in Railway dashboard
- Or use CLI: `railway logs`

**Render:**
- View logs in Render dashboard

**Fly.io:**
- `flyctl logs`

## Next Steps

1. ✅ Register GitHub App
2. ✅ Deploy to Railway/Render
3. ✅ Install on test repository
4. ✅ Create test PR
5. ✅ Verify comments posted
6. ✅ Install on production repositories
7. 🎉 Enjoy automated accessibility reviews!

## Support

For issues or questions:
- GitHub Issues: https://github.com/dominiclabbe/accessibility-fixer/issues
- Documentation: https://github.com/dominiclabbe/accessibility-fixer

## Architecture

See [GITHUB_APP_DESIGN.md](GITHUB_APP_DESIGN.md) for detailed architecture documentation.
