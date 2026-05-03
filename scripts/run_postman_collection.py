"""
Execute Break Free Postman collection v2.1 against a running server.
Usage: .venv\\Scripts\\python scripts/run_postman_collection.py [--base-url URL]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import uuid
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent


def load_collection(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def get_variables(collection: dict) -> dict:
    out = {}
    for v in collection.get("variable", []):
        out[v["key"]] = v.get("value", "")
    return out


def substitute(s: str, vars_: dict) -> str:
    if not isinstance(s, str):
        return s
    for k, v in vars_.items():
        s = s.replace(f"{{{{{k}}}}}", str(v))
    return s


def build_request(item: dict, vars_: dict) -> tuple[str, str, dict, str | None]:
    req = item["request"]
    method = req["method"].upper()
    url = substitute(req["url"], vars_)
    if isinstance(url, str) and not url.startswith("http"):
        url = vars_["base_url"].rstrip("/") + "/" + url.lstrip("/")
    headers = {}
    for h in req.get("header", []):
        if h.get("disabled"):
            continue
        headers[h["key"]] = substitute(h["value"], vars_)
    body = None
    b = req.get("body")
    if b and b.get("mode") == "raw":
        body = substitute(b.get("raw", ""), vars_)
    return method, url, headers, body


def patch_body_dict(bd: dict, test_user: str, test_email: str) -> None:
    if not isinstance(bd, dict):
        return
    if bd.get("email") == "rasel@example.com":
        bd["email"] = test_email
    if bd.get("username") == "rasel":
        bd["username"] = test_user


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default=None)
    ap.add_argument("--collection", type=Path, default=ROOT / "postman_collection.json")
    args = ap.parse_args()

    collection = load_collection(args.collection)
    vars_ = get_variables(collection)
    if args.base_url:
        vars_["base_url"] = args.base_url.rstrip("/")

    session = requests.Session()
    results: list[tuple[str, int, str]] = []
    notification_id: str | None = None
    guest_device_mood = f"guest-mood-{uuid.uuid4().hex[:12]}"
    guest_device_forecast = f"guest-ff-{uuid.uuid4().hex[:12]}"

    test_user = f"pm_runner_{uuid.uuid4().hex[:8]}"
    test_pass = "TestRunner123!"
    test_email = f"{test_user}@example.com"

    reg = session.post(
        f"{vars_['base_url']}/api/auth/register/",
        json={
            "username": test_user,
            "email": test_email,
            "full_name": "Postman Runner",
            "phone": "01700000001",
            "password": test_pass,
        },
        headers={"Content-Type": "application/json"},
        timeout=30,
    )
    if reg.status_code not in (200, 201):
        print("FATAL: register failed:", reg.status_code, reg.text[:400])
        return 1

    login = session.post(
        f"{vars_['base_url']}/api/auth/login/",
        json={"username": test_user, "password": test_pass},
        headers={"Content-Type": "application/json"},
        timeout=30,
    )
    if login.status_code != 200:
        print("FATAL: login failed:", login.status_code, login.text[:400])
        return 1

    tok = login.json().get("access")
    if not tok:
        print("FATAL: no access token", login.text[:400])
        return 1
    vars_["access_token"] = tok

    auth_h = {"Authorization": f"Bearer {tok}"}
    wp = session.get(f"{vars_['base_url']}/api/subscription-plans/", headers=auth_h, timeout=30).json()
    pp = session.get(f"{vars_['base_url']}/api/premium/plans/", timeout=30).json()
    vars_["wellness_plan_id"] = str(wp[0]["id"]) if isinstance(wp, list) and wp else vars_.get("wellness_plan_id", "1")
    vars_["premium_plan_id"] = str(pp[0]["id"]) if isinstance(pp, list) and pp else vars_.get("premium_plan_id", "1")

    for item in collection["item"]:
        name = item["name"]
        method, url, headers, body = build_request(item, vars_)
        body_json = None
        raw_data = None

        if name == "Auth - Register":
            results.append((name, 299, "SKIP (already registered runner user)"))
            continue

        if name == "Auth - Login":
            body_json = {"username": test_user, "password": test_pass}
        elif body:
            try:
                body_json = json.loads(body)
                patch_body_dict(body_json, test_user, test_email)
            except json.JSONDecodeError:
                raw_data = body

        if notification_id:
            url = url.replace("/api/notifications/1/", f"/api/notifications/{notification_id}/")

        if name == "Guest - Log Mood (X-Device-Id)":
            headers = dict(headers)
            headers["X-Device-Id"] = guest_device_mood
        if name == "Guest - Fear Forecast":
            headers = dict(headers)
            headers["X-Device-Id"] = guest_device_forecast

        send_kw: dict = {"method": method, "url": url, "headers": headers, "timeout": 45}
        if body_json is not None:
            send_kw["json"] = body_json
        elif raw_data is not None:
            send_kw["data"] = raw_data

        resp = session.request(**send_kw)
        code = resp.status_code
        err = ""

        if code in (200, 201) and "application/json" in resp.headers.get("content-type", ""):
            try:
                data = resp.json()
                if name == "Notifications - Create" and isinstance(data, dict) and data.get("id"):
                    notification_id = str(data["id"])
            except json.JSONDecodeError:
                pass

        if code >= 400:
            err = (resp.text or "")[:350].replace("\n", " ")

        results.append((name, code, err))

    failures = [(n, c, e) for n, c, e in results if c >= 400 and "SKIP" not in e]
    skips = [r for r in results if "SKIP" in r[2]]

    print("\n=== Postman collection run ===\n")
    for name, code, extra in results:
        skip = "SKIP" in extra
        ok = code < 400 or skip
        label = "OK " if ok else "FAIL"
        line = f"[{label}] {code:3d}  {name}"
        if extra and not skip and not ok:
            line += f"  |  {extra}"
        elif skip:
            line += f"  |  {extra}"
        print(line)

    print(f"\nTotal: {len(results)}  HTTP failures: {len(failures)}  Skipped: {len(skips)}")
    if failures:
        print("\n--- Failure summary ---")
        for n, c, e in failures:
            print(f"  {c}  {n}: {e[:200]}")
    return 1 if failures else 0


if __name__ == "__main__":
    time.sleep(0.5)
    sys.exit(main())
