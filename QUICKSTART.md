# Quick Start - 30 Minutes to Working GitHub App

Follow these steps to get your accessibility reviewer running.

## Prerequisites Check

```bash
# Check you have these:
python --version    # Need 3.11+
pip --version       # Need pip
gh --version        # Need GitHub CLI

# If missing GitHub CLI:
brew install gh
```

## Step 1: Install Dependencies (2 minutes)

```bash
cd /Users/dominiclabbe/dev/accessibility-fixer

# Install Python packages
pip install -r requirements-app.txt
```

Expected output:
```
Successfully installed flask gunicorn PyGithub pyjwt cryptography openai anthropic...
```

## Step 2: Configure Environment (5 minutes)

### Create .env file

```bash
# Copy template
cp .env.example .env

# Open in editor
code .env  # or nano .env
```

### Fill in Scout credentials (you already have these)

```bash
# .env
SCOUT_API_KEY=your-scout-api-key-here
SCOUT_BASE_URL=https://interne.scout.mirego.com/api/chat/openai_compatible
SCOUT_MODEL=gpt-5.2

# Leave these empty for now (we'll fill after GitHub App registration)
GITHUB_APP_ID=
GITHUB_APP_PRIVATE_KEY=
GITHUB_WEBHOOK_SECRET=

PORT=8080
```

**Save the file.**

## Step 3: Test Server Works (2 minutes)

```bash
# Run server
python app/webhook_server.py
```

Expected output:
```
Starting Accessibility Reviewer GitHub App
Port: 8080
Webhook secret configured: False
GitHub auth configured: False
PR reviewer configured: True  ← This should be True!
 * Running on http://0.0.0.0:8080
```

**Test health check:**

Open another terminal:
```bash
curl http://localhost:8080/health
```

Expected:
```json
{
  "status": "degraded",
  "checks": {
    "webhook_secret": false,
    "github_auth": false,
    "pr_reviewer": true
  }
}
```

✅ If you see this, server works! (degraded is OK, we haven't configured GitHub App yet)

**Stop server:** Press `Ctrl+C`

## Step 4: Register GitHub App (10 minutes)

### 4.1 Generate Webhook Secret

```bash
# Generate random secret
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output (something like: `a1b2c3d4e5f6...`)

Save this somewhere - you'll need it twice:
1. In GitHub App settings
2. In your .env file

### 4.2 Start ngrok (for testing)

```bash
# In a new terminal
ngrok http 8080
```

You'll see:
```
Forwarding  https://abc123.ngrok.io -> http://localhost:8080
```

**Copy the https URL** (e.g., `https://abc123.ngrok.io`)

### 4.3 Create GitHub App

**Go to:** https://github.com/settings/apps/new

**Fill in:**

| Field | Value |
|-------|-------|
| **GitHub App name** | `Accessibility Reviewer - [YOUR NAME]` |
| **Homepage URL** | `https://github.com/dominiclabbe/accessibility-fixer` |
| **Webhook URL** | `https://abc123.ngrok.io/webhook` (your ngrok URL + /webhook) |
| **Webhook secret** | Paste the secret you generated |

**Permissions (Repository permissions):**
- **Pull requests**: `Read & Write` ✅
- **Contents**: `Read` ✅
- **Commit statuses**: `Read & Write` ✅
- **Metadata**: `Read` ✅ (auto-selected)

**Subscribe to events:**
- ☑️ **Pull request** ✅

**Where can this app be installed?**
- Select: **"Any account"**

**Click:** "Create GitHub App"

### 4.4 Generate Private Key

After creation:
1. Scroll down to **"Private keys"**
2. Click **"Generate a private key"**
3. A `.pem` file downloads
4. **Save this file!** You'll need it next

### 4.5 Note Your App ID

At the top of the page, you'll see:
```
App ID: 123456
```

**Copy this number.**

## Step 5: Update .env File (3 minutes)

```bash
# Open .env again
code .env
```

**Update these fields:**

```bash
GITHUB_APP_ID=123456  # Your App ID from above

# For the private key, open the .pem file and copy ENTIRE contents
GITHUB_APP_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA...
...paste entire key...
...keep all the lines...
-----END RSA PRIVATE KEY-----"

GITHUB_WEBHOOK_SECRET=a1b2c3d4e5f6...  # The secret you generated

SCOUT_API_KEY=your-scout-key
SCOUT_BASE_URL=https://interne.scout.mirego.com/api/chat/openai_compatible
SCOUT_MODEL=gpt-5.2

PORT=8080
```

**Important:**
- The private key must have actual newlines (not `\n`)
- Include the BEGIN and END lines
- Keep it in quotes

**Save the file.**

## Step 6: Test Locally with ngrok (5 minutes)

### 6.1 Start Server

```bash
python app/webhook_server.py
```

Now you should see:
```
Starting Accessibility Reviewer GitHub App
Port: 8080
Webhook secret configured: True   ← Now True!
GitHub auth configured: True       ← Now True!
PR reviewer configured: True
 * Running on http://0.0.0.0:8080
```

**All three should be True!** ✅

### 6.2 Test Health

```bash
curl http://localhost:8080/health
```

Should return:
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

✅ **"healthy"** means it's working!

### 6.3 Install App on Test Repo

**Go to:** https://github.com/apps/accessibility-reviewer-yourname (your app page)

**Click:** "Install App"

**Select:** `multiplatform_test_app` repository

**Click:** "Install"

### 6.4 Create Test PR

```bash
cd /Users/dominiclabbe/dev/multiplatform_test_app

# Create test branch
git checkout -b test/github-app-local

# Create file with accessibility issue
cat > androidApp/src/main/java/TestButton.kt << 'EOF'
package com.example.app

import androidx.compose.material.IconButton
import androidx.compose.material.Icon
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Star
import androidx.compose.runtime.Composable

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
git push origin test/github-app-local

# Create PR
gh pr create --title "Test: GitHub App Review" --body "Testing accessibility review with GitHub App"
```

### 6.5 Watch the Magic! ✨

**In your server terminal**, you should see:
```
Received webhook: pull_request
Processing PR #X: Test: GitHub App Review
Changed files: 1
Detected platforms: ['Android']
Loading accessibility guides...
Starting accessibility review...
Found 1 accessibility issues
Posting review comments...
✅ Review complete
```

**On GitHub**, check your PR:
- You should see a comment from your app!
- It should have an inline comment on line 9 (contentDescription = null)
- It should say something like "🔴 Missing accessibility label"

🎉 **IT WORKS!**

## Step 7: Deploy to Railway (3 minutes)

Now let's make it permanent (no more ngrok).

### 7.1 Create Railway Account

**Go to:** https://railway.app

**Sign up** with GitHub

### 7.2 Create New Project

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Select **`dominiclabbe/accessibility-fixer`**
4. Railway will start deploying

### 7.3 Add Environment Variables

In Railway dashboard:
1. Click **"Variables"** tab
2. Click **"Raw Editor"**
3. Paste your entire `.env` file content:

```bash
GITHUB_APP_ID=123456
GITHUB_APP_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----
...your entire key...
-----END RSA PRIVATE KEY-----"
GITHUB_WEBHOOK_SECRET=your-secret
SCOUT_API_KEY=your-scout-key
SCOUT_BASE_URL=https://interne.scout.mirego.com/api/chat/openai_compatible
SCOUT_MODEL=gpt-5.2
PORT=8080
```

4. Click **"Update Variables"**

Railway will redeploy automatically.

### 7.4 Get Railway URL

After deployment completes:
1. Click **"Settings"** tab
2. Under **"Domains"**, you'll see something like:
   ```
   accessibility-fixer.railway.app
   ```
3. **Copy this URL**

### 7.5 Update GitHub App Webhook URL

**Go to:** Your GitHub App settings
- https://github.com/settings/apps/accessibility-reviewer-yourname

**Update:**
- **Webhook URL**: Change from ngrok to Railway:
  ```
  https://accessibility-fixer.railway.app/webhook
  ```

**Click:** "Save changes"

### 7.6 Test Again

Create another test PR (or close/reopen the existing one):

```bash
cd /Users/dominiclabbe/dev/multiplatform_test_app

git checkout main
git checkout -b test/github-app-production

# Add another file
cat > androidApp/src/main/java/TestButton2.kt << 'EOF'
package com.example.app

import androidx.compose.material.Button
import androidx.compose.material.Text
import androidx.compose.runtime.Composable

@Composable
fun TestButton2() {
    Button(onClick = { }) {
        // Missing accessible label
    }
}
EOF

git add .
git commit -m "Test: Empty button"
git push origin test/github-app-production

gh pr create --title "Test: Production Deployment" --body "Testing with Railway deployment"
```

**Check Railway Logs:**
1. Go to Railway dashboard
2. Click "Deployments" tab
3. Click latest deployment
4. Click "View Logs"
5. You should see the review process

**Check PR on GitHub:**
- Should see review comments from your app!

🎉 **NOW IT'S PERMANENT!** No more ngrok needed.

## Step 8: Install on More Repos (1 minute)

Now you can install your app on any repository:

**Go to:** https://github.com/apps/accessibility-reviewer-yourname

**Click:** "Configure"

**Select repositories** you want to review

**Click:** "Save"

✅ **Done!** Your app will now review PRs on all selected repos.

## Troubleshooting

### Server says "PR reviewer configured: False"

**Problem:** Scout credentials missing or invalid

**Fix:**
```bash
# Check .env has:
SCOUT_API_KEY=...  # Not empty
SCOUT_BASE_URL=https://interne.scout.mirego.com/api/chat/openai_compatible
```

### Webhook not received

**Problem:** Wrong webhook URL or secret

**Fix:**
1. Check GitHub App settings → Webhook URL is correct
2. Check webhook secret matches `.env`
3. Check webhook deliveries in GitHub App settings (shows errors)

### "Invalid signature" error

**Problem:** Webhook secret mismatch

**Fix:**
```bash
# Regenerate secret
python -c "import secrets; print(secrets.token_hex(32))"

# Update in both:
# 1. GitHub App settings
# 2. .env file (or Railway variables)
```

### Railway deployment fails

**Problem:** Missing environment variables

**Fix:**
1. Check all variables are set in Railway
2. Check private key has proper newlines
3. Check Railway logs for specific error

### No comments posted on PR

**Check:**
1. Railway logs - any errors?
2. GitHub App permissions - "Pull requests: Read & Write"?
3. Installation - App installed on the repo?
4. Changed files - Are they UI files (.kt, .swift, .tsx)?

## Quick Reference

### Restart Server (Local)
```bash
# Stop: Ctrl+C
# Start:
python app/webhook_server.py
```

### View Railway Logs
```bash
# Install Railway CLI
brew install railway

# Login
railway login

# View logs
railway logs
```

### Update Environment Variables
```bash
# Railway dashboard → Variables → Update
# App will auto-redeploy
```

### Test Webhook Manually
```bash
# Check webhook deliveries
# GitHub App settings → Advanced → Recent Deliveries
# Click a delivery → "Redeliver" to test again
```

## Success Checklist

- [x] Server runs locally with all checks "True"
- [x] Health endpoint returns "healthy"
- [x] ngrok test works (comment posted on PR)
- [x] Railway deployment succeeds
- [x] Production test works (comment posted)
- [x] App installed on desired repos

## What's Next?

Your GitHub App is now running! Every time someone creates/updates a PR:
1. Your app receives webhook
2. Reviews code for accessibility issues
3. Posts inline comments
4. Updates commit status

**Optional enhancements** (later):
- Add bot conversations (`@accessibility-bot`)
- Skip simple changes (save costs)
- PR summaries
- See: `ENHANCEMENT_IDEAS.md`

## Maintenance

**Monthly:** Check Railway dashboard
- Monitor usage
- Check logs for errors

**As needed:**
- Update guides in `guides/` folder
- Push to GitHub → Railway auto-deploys

**That's it!** Minimal maintenance required. 🎉
