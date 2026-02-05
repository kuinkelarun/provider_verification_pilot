# Databricks App Configuration & Secrets Management

## Problem
When pulling changes from GitHub, `app.yaml` gets overwritten and your Databricks secrets are lost, requiring manual re-entry.

## Solution: Use gitignore + Template File ✅ (Recommended)

### Quick Setup

1. **Your local `app.yaml` is now protected from git**
   - `app.yaml` has been added to `.gitignore`
   - Git will never overwrite your local secrets on pull

2. **Copy the template file**
   ```bash
   cp app.yaml.example app.yaml
   ```

3. **Fill in your secrets in `app.yaml`**
   ```yaml
   - name: DATABRICKS_HOST
     value: "https://your-workspace.cloud.databricks.com"
   - name: DATABRICKS_TOKEN
     value: "your-personal-access-token"
   - name: DATABRICKS_HTTP_PATH
     value: "/sql/1.0/warehouses/your-warehouse-id"
   ```

4. **Never commit `app.yaml` to git**
   - Only `app.yaml.example` is committed
   - Your secrets stay safe locally

### Benefits
- ✅ Secrets never committed to version control
- ✅ Pull/push won't overwrite your configuration
- ✅ Template file helps new developers set up
- ✅ Works across development, staging, production

---

## Alternative Solutions

### Option 2: Use Databricks Secrets Manager (Production)

Store secrets in Databricks instead of the file:

```yaml
env:
  - name: DATABRICKS_HOST
    value: "{{secrets/databricks/host}}"
  - name: DATABRICKS_TOKEN
    value: "{{secrets/databricks/token}}"
```

**Setup in Databricks:**
1. Go to Workspace Settings > Secrets
2. Create secret scope "databricks"
3. Add secrets: `host`, `token`, `http_path`

### Option 3: Use Environment Variables (Development)

In production, load from environment at runtime:

```python
# app.py
import os

DATABRICKS_HOST = os.getenv('DATABRICKS_HOST')
DATABRICKS_TOKEN = os.getenv('DATABRICKS_TOKEN')
```

Set variables before running Flask:
```bash
export DATABRICKS_HOST="your-host"
export DATABRICKS_TOKEN="your-token"
python app.py
```

### Option 4: Use .env File (Local Development)

1. Create `.env` file (already in `.gitignore`)
   ```
   DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
   DATABRICKS_TOKEN=your-personal-access-token
   DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/warehouse-id
   ```

2. Load in `app.py`:
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

---

## Recommended Workflow

### Local Development
- Use `app.yaml` locally (protected by `.gitignore`)
- Use `.env` for sensitive values
- Never commit secrets

### Production (Databricks Apps)
- Use Databricks Secrets Manager
- Reference secrets in `app.yaml.example` or environment
- Store `app.yaml` in Databricks Apps UI (it will be secured)

---

## Getting Databricks Credentials

1. **DATABRICKS_HOST**
   - Go to Workspace > Settings > Admin Settings > Workspace URLs
   - Copy your Workspace URL (e.g., `https://dbc-abc123.cloud.databricks.com`)

2. **DATABRICKS_TOKEN**
   - Go to Settings > Developer Settings > Personal access tokens
   - Click "Generate new token"
   - Copy the token (⚠️ Keep this secret!)

3. **DATABRICKS_HTTP_PATH**
   - Go to Compute > SQL Warehouses
   - Select your warehouse
   - Click "Connection Details"
   - Copy the HTTP Path (e.g., `/sql/1.0/warehouses/abc123def456`)

---

## Verification Checklist

- [ ] `.gitignore` includes `app.yaml`
- [ ] `app.yaml.example` is committed to git
- [ ] `app.yaml` is in `.git/info/exclude` or `.gitignore`
- [ ] Your local `app.yaml` has filled-in secrets
- [ ] You can pull from GitHub without losing secrets
- [ ] Sensitive values are never in git history

---

## FAQ

**Q: What if I already committed `app.yaml` with secrets?**
A: Remove from git history:
```bash
# Remove from git (only)
git rm --cached app.yaml
# Add to .gitignore
echo "app.yaml" >> .gitignore
# Commit the removal
git commit -m "Remove app.yaml from tracking"
# Force push to update remote
git push --force-with-lease
```

**Q: Can team members access the secrets?**
A: Yes, use Databricks Secrets Manager or a secret management tool like:
- AWS Secrets Manager
- HashiCorp Vault
- Azure Key Vault
- 1Password / LastPass (team shares)

**Q: How do I prevent accidental commits?**
A: Add a pre-commit hook:
```bash
# Create .git/hooks/pre-commit
#!/bin/bash
if git diff --cached --name-only | grep -q "^app.yaml$"; then
    echo "ERROR: Do not commit app.yaml!"
    exit 1
fi
```

---

## Summary
Your `app.yaml` is now protected from git. Use `app.yaml.example` as a template for configuration, and your local secrets will persist across pulls from GitHub.
