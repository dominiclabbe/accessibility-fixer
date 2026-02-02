# Multi-Provider AI Setup Guide

The PR review system now supports **multiple AI providers**! Choose the one that works best for you.

## 🎯 Supported Providers

| Provider | Model | API Key | Cost | Setup Difficulty |
|----------|-------|---------|------|------------------|
| **GitHub Models** | GPT-4o, Claude 3.5 | GitHub Token | Low/Free | ⭐ Easy |
| **Anthropic** | Claude Sonnet 4 | Anthropic API | ~$10-50/mo | ⭐⭐ Medium |
| **OpenAI** | GPT-4 | OpenAI API | ~$20-100/mo | ⭐⭐ Medium |

## 🚀 Quick Start

### Option 1: GitHub Models (Recommended - Easiest!)

**Advantages:**
- ✅ Uses your existing `GITHUB_TOKEN` (no separate API key!)
- ✅ Multiple models available (GPT-4o, Claude, Mistral)
- ✅ Lower cost or free tier
- ✅ Built into GitHub Actions

**Setup:**

1. **Copy workflow file:**
```bash
cp /path/to/accessibility-fixer/ci-examples/github-actions-github-models.yml \
   .github/workflows/accessibility-pr-review.yml
```

2. **That's it!** No API key needed. Uses `GITHUB_TOKEN` automatically.

3. **Optional:** Choose a model by editing the workflow:
```yaml
env:
  AI_PROVIDER: github
  GITHUB_MODEL: gpt-4o  # or claude-3-5-sonnet, gpt-4o-mini
```

### Option 2: Anthropic Claude

**Advantages:**
- ✅ Highest quality (Claude Sonnet 4)
- ✅ Best for complex accessibility analysis
- ✅ Production-proven

**Setup:**

1. **Get API key:** https://console.anthropic.com/

2. **Add to GitHub:**
```bash
gh secret set ANTHROPIC_API_KEY
```

3. **Copy workflow:**
```bash
cp /path/to/accessibility-fixer/ci-examples/github-actions-anthropic.yml \
   .github/workflows/accessibility-pr-review.yml
```

### Option 3: OpenAI

**Advantages:**
- ✅ GPT-4 available
- ✅ Well-documented
- ✅ Widely supported

**Setup:**

1. **Get API key:** https://platform.openai.com/

2. **Add to GitHub:**
```bash
gh secret set OPENAI_API_KEY
```

3. **Use multi-provider script with OpenAI:**
```yaml
env:
  AI_PROVIDER: openai
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

## 📋 Configuration Options

### Environment Variables

| Variable | Required | Default | Options |
|----------|----------|---------|---------|
| `AI_PROVIDER` | No | `anthropic` | `anthropic`, `github`, `openai` |
| `ANTHROPIC_API_KEY` | If using Anthropic | - | Your Anthropic API key |
| `GITHUB_TOKEN` | If using GitHub Models | Auto-set | GitHub Actions token |
| `OPENAI_API_KEY` | If using OpenAI | - | Your OpenAI API key |

### Model Selection

**Anthropic Models:**
```yaml
ANTHROPIC_MODEL: claude-sonnet-4-20250514  # Default
# or: claude-opus-4-20250514 (more expensive, higher quality)
```

**GitHub Models:**
```yaml
GITHUB_MODEL: gpt-4o  # Default
# Options:
# - gpt-4o (GPT-4 Optimized, best balance)
# - gpt-4o-mini (Faster, cheaper)
# - claude-3-5-sonnet (Claude on GitHub - if available)
# - mistral-large (Mistral AI)
```

**OpenAI Models:**
```yaml
OPENAI_MODEL: gpt-4  # Default
# Options:
# - gpt-4 (Best quality)
# - gpt-4-turbo (Faster)
# - gpt-3.5-turbo (Cheapest)
```

## 💰 Cost Comparison

### Per PR (Estimated)

| Provider | Small PR | Medium PR | Large PR | Monthly* |
|----------|----------|-----------|----------|----------|
| **GitHub Models** | $0.05-0.10 | $0.10-0.25 | $0.25-0.50 | $5-25 |
| **Anthropic Claude** | $0.10-0.20 | $0.20-0.50 | $0.50-1.00 | $10-50 |
| **OpenAI GPT-4** | $0.15-0.30 | $0.30-0.75 | $0.75-1.50 | $15-75 |

*Based on 50 PRs/month

**Note:** GitHub Models may have free tier or lower pricing. Check current pricing.

## 🔧 Complete Workflow Example

```yaml
name: Accessibility PR Review

on:
  pull_request:
    types: [opened, synchronize, reopened]

permissions:
  pull-requests: write
  contents: read

jobs:
  accessibility-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Setup framework
        run: |
          git clone https://github.com/dominiclabbe/accessibility-fixer.git /tmp/accessibility-fixer
          pip install -r /tmp/accessibility-fixer/scripts/requirements-multi.txt
          echo "${{ secrets.GITHUB_TOKEN }}" | gh auth login --with-token

      - name: Run review
        env:
          # Choose your provider:
          AI_PROVIDER: github  # or 'anthropic' or 'openai'

          # Provider-specific keys:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          # ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          # OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}

          # Optional model selection:
          GITHUB_MODEL: gpt-4o
          # ANTHROPIC_MODEL: claude-sonnet-4-20250514
          # OPENAI_MODEL: gpt-4

          PR_NUMBER: ${{ github.event.pull_request.number }}
          GITHUB_REPOSITORY: ${{ github.repository }}
          FRAMEWORK_PATH: /tmp/accessibility-fixer
        run: python /tmp/accessibility-fixer/scripts/pr-review-ci-multi.py
```

## 🎯 Which Provider Should I Use?

### Use GitHub Models if:
- ✅ You want the easiest setup (no separate API key)
- ✅ You want lower costs
- ✅ You're already using GitHub Actions
- ✅ GPT-4o quality is sufficient

### Use Anthropic if:
- ✅ You want the highest quality analysis
- ✅ You need Claude Sonnet 4 specifically
- ✅ Accessibility accuracy is critical
- ✅ You're okay with separate API key

### Use OpenAI if:
- ✅ You already have OpenAI credits
- ✅ You prefer GPT-4
- ✅ You want flexibility with model choice

## 📊 Quality Comparison

Based on accessibility review accuracy:

| Provider | Model | Accuracy | Speed | Cost |
|----------|-------|----------|-------|------|
| Anthropic | Claude Sonnet 4 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| GitHub | GPT-4o | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| GitHub | Claude 3.5 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| OpenAI | GPT-4 | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |

**Recommendation:** Start with GitHub Models (gpt-4o or claude-3-5-sonnet). Switch to Anthropic if you need higher accuracy.

## 🔄 Switching Providers

Easy! Just change one environment variable:

```yaml
# From GitHub Models:
env:
  AI_PROVIDER: github
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

# To Anthropic:
env:
  AI_PROVIDER: anthropic
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

No code changes needed!

## 🧪 Testing Different Providers

Try them side-by-side:

```yaml
jobs:
  review-github:
    runs-on: ubuntu-latest
    steps:
      - # ... setup steps ...
      - name: Review with GitHub Models
        env:
          AI_PROVIDER: github
        run: python /tmp/accessibility-fixer/scripts/pr-review-ci-multi.py

  review-anthropic:
    runs-on: ubuntu-latest
    steps:
      - # ... setup steps ...
      - name: Review with Anthropic
        env:
          AI_PROVIDER: anthropic
        run: python /tmp/accessibility-fixer/scripts/pr-review-ci-multi.py
```

Compare the results and pick your favorite!

## 🐛 Troubleshooting

### "Unknown AI_PROVIDER"

Check spelling:
```yaml
AI_PROVIDER: github  # ✅ lowercase
AI_PROVIDER: GitHub  # ❌ wrong case
```

### "GITHUB_TOKEN not set" (GitHub Models)

Ensure permissions:
```yaml
permissions:
  pull-requests: write  # Required!
```

### "API key not set"

For Anthropic/OpenAI, verify secret:
```bash
gh secret list  # Check if secret exists
gh secret set ANTHROPIC_API_KEY  # Add if missing
```

### "Model not found"

Check available models:
- **GitHub Models:** https://github.com/marketplace/models
- **Anthropic:** claude-sonnet-4-20250514, claude-opus-4-20250514
- **OpenAI:** gpt-4, gpt-4-turbo, gpt-3.5-turbo

### GitHub Models 404 error

GitHub Models may be in preview. Ensure:
1. You have access to GitHub Models preview
2. The model name is correct
3. Your token has proper permissions

## 📚 Resources

### Provider Documentation
- **GitHub Models:** https://github.com/marketplace/models
- **Anthropic:** https://docs.anthropic.com/
- **OpenAI:** https://platform.openai.com/docs

### Script Documentation
- **Multi-Provider Script:** `scripts/pr-review-ci-multi.py`
- **Original Script:** `scripts/pr-review-ci.py` (Anthropic only)
- **Requirements:** `scripts/requirements-multi.txt`

### Workflow Examples
- **GitHub Models:** `ci-examples/github-actions-github-models.yml`
- **Anthropic:** `ci-examples/github-actions-anthropic.yml`
- **Original:** `ci-examples/github-actions-with-api.yml`

## 🎉 Benefits of Multi-Provider

- ✅ **Flexibility:** Switch providers anytime
- ✅ **Cost Control:** Use cheaper options when suitable
- ✅ **Quality Options:** Use premium models for critical PRs
- ✅ **Redundancy:** Fallback if one provider has issues
- ✅ **Comparison:** Test multiple providers side-by-side

## 💡 Best Practices

1. **Start Simple:** Begin with GitHub Models (easiest)
2. **Monitor Costs:** Track API usage
3. **Compare Quality:** Test different models
4. **Set Limits:** Use branch protection to control usage
5. **Document Choice:** Note which provider/model you're using

---

**Choose what works best for your team and budget!** 🚀
