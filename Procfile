web: gunicorn run:app

# ===== railway.json (Optional) =====
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn run:app",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}

# ===== runtime.txt (Optional, specify Python version) =====
python-3.11.0

# ===== nixpacks.toml (Alternative build config) =====
[phases.setup]
nixPkgs = ["python311", "postgresql"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[start]
cmd = "gunicorn run:app"