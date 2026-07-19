import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
os.environ["USE_SQLITE"] = "true"
os.environ.setdefault("SECRET_KEY", "dev-secret-key-at-least-32-characters")

import django

django.setup()

from apps.tools_registry.discovery import load_tool_plugins
from django.test import Client

print("plugins", sorted(load_tool_plugins().keys()))
c = Client()
r = c.get("/api/v1/tools/")
payload = r.json()
data = payload.get("data") or payload.get("results") or []
print("tools status", r.status_code, "count", len(data))
r2 = c.post(
    "/api/v1/t/json-formatter/",
    data='{"action":"format","json":"{\\"a\\":1}"}',
    content_type="application/json",
)
print("json-formatter", r2.status_code, r2.content[:300])
