#!/usr/bin/env python3
"""Small read-oriented Odoo XML-RPC query helper for Hermes.

Credentials are loaded from environment variables first, then from the Hermes
profile .env file (usually /opt/data/.env in this gateway profile).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import xmlrpc.client
from pathlib import Path
from typing import Any


def _load_dotenv() -> None:
    candidates = []
    if os.getenv("HERMES_HOME"):
        candidates.append(Path(os.environ["HERMES_HOME"]) / ".env")
    candidates.extend([Path("/opt/data/.env"), Path.home() / ".hermes" / ".env", Path.home() / ".env"])
    for path in candidates:
        if not path.exists():
            continue
        try:
            for line in path.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = val
        except Exception:
            pass


def _json_loads(value: str, default: Any) -> Any:
    if value is None or value == "":
        return default
    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON: {exc}: {value}")


def _config() -> dict[str, str]:
    _load_dotenv()
    cfg = {
        "url": os.getenv("ODOO19_URL", "").rstrip("/"),
        "db": os.getenv("ODOO19_DB", ""),
        "user": os.getenv("ODOO19_USER", ""),
        "password": os.getenv("ODOO19_PASSWORD", ""),
    }
    missing = [k for k, v in cfg.items() if not v]
    if missing:
        raise SystemExit("Missing Odoo config: " + ", ".join("ODOO19_" + k.upper() for k in missing))
    return cfg


def _connect():
    cfg = _config()
    common = xmlrpc.client.ServerProxy(f"{cfg['url']}/xmlrpc/2/common", allow_none=True)
    uid = common.authenticate(cfg["db"], cfg["user"], cfg["password"], {})
    if not uid:
        raise SystemExit("Authentication failed")
    models = xmlrpc.client.ServerProxy(f"{cfg['url']}/xmlrpc/2/object", allow_none=True)
    return cfg, uid, models, common


def _execute_kw(model: str, method: str, args: list[Any] | None = None, kwargs: dict[str, Any] | None = None) -> Any:
    cfg, uid, models, _common = _connect()
    return models.execute_kw(cfg["db"], uid, cfg["password"], model, method, args or [], kwargs or {})


def cmd_ping(_args):
    cfg, uid, _models, common = _connect()
    print(json.dumps({"ok": True, "url": cfg["url"], "db": cfg["db"], "uid": uid, "version": common.version()}, indent=2, default=str))


def cmd_models(args):
    domain = []
    if args.search:
        domain = [["model", "ilike", args.search]]
    result = _execute_kw("ir.model", "search_read", [domain], {"fields": ["model", "name"], "limit": args.limit, "order": "model asc"})
    print(json.dumps(result, indent=2, default=str))


def cmd_fields(args):
    result = _execute_kw(args.model, "fields_get", [], {"attributes": ["string", "type", "relation", "required", "readonly", "help"]})
    items = [{"name": k, **v} for k, v in result.items()]
    if args.search:
        q = args.search.lower()
        items = [x for x in items if q in x.get("name", "").lower() or q in str(x.get("string", "")).lower()]
    items.sort(key=lambda x: x["name"])
    print(json.dumps(items[: args.limit], indent=2, default=str))


def cmd_count(args):
    domain = _json_loads(args.domain, [])
    result = _execute_kw(args.model, "search_count", [domain])
    print(json.dumps({"model": args.model, "domain": domain, "count": result}, indent=2, default=str))


def cmd_search_read(args):
    domain = _json_loads(args.domain, [])
    fields = [x.strip() for x in args.fields.split(",") if x.strip()] if args.fields else []
    kwargs = {"limit": args.limit, "offset": args.offset}
    if fields:
        kwargs["fields"] = fields
    if args.order:
        kwargs["order"] = args.order
    result = _execute_kw(args.model, "search_read", [domain], kwargs)
    print(json.dumps(result, indent=2, default=str))


def cmd_read(args):
    ids = _json_loads(args.ids, [])
    if isinstance(ids, int):
        ids = [ids]
    fields = [x.strip() for x in args.fields.split(",") if x.strip()] if args.fields else []
    kwargs = {"fields": fields} if fields else {}
    result = _execute_kw(args.model, "read", [ids], kwargs)
    print(json.dumps(result, indent=2, default=str))


def main() -> int:
    parser = argparse.ArgumentParser(description="Query Odoo 19 via XML-RPC")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("ping")
    p.set_defaults(func=cmd_ping)

    p = sub.add_parser("models")
    p.add_argument("--search", default="")
    p.add_argument("--limit", type=int, default=50)
    p.set_defaults(func=cmd_models)

    p = sub.add_parser("fields")
    p.add_argument("model")
    p.add_argument("--search", default="")
    p.add_argument("--limit", type=int, default=200)
    p.set_defaults(func=cmd_fields)

    p = sub.add_parser("count")
    p.add_argument("model")
    p.add_argument("--domain", default="[]")
    p.set_defaults(func=cmd_count)

    p = sub.add_parser("search-read")
    p.add_argument("model")
    p.add_argument("--domain", default="[]")
    p.add_argument("--fields", default="")
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--offset", type=int, default=0)
    p.add_argument("--order", default="")
    p.set_defaults(func=cmd_search_read)

    p = sub.add_parser("read")
    p.add_argument("model")
    p.add_argument("ids", help="JSON id or list of ids, e.g. 5 or [5,6]")
    p.add_argument("--fields", default="")
    p.set_defaults(func=cmd_read)

    args = parser.parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
