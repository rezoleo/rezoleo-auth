import logging
import os
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

app = FastAPI()

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
ZITADEL_CONSOLE_URL = os.getenv("ZITADEL_CONSOLE_URL")


@app.post("/on-user-created")
async def new_user(payload: dict[str, Any]):
    logging.info(f"New user created: {payload}")

    user_id = payload["response"]["userId"]
    organization_id = payload["response"]["resourceOwner"]

    message = {
        "embeds": [
            {
                "id": 231387627,
                "description": f"{ZITADEL_CONSOLE_URL}/users/{user_id}",
                "fields": [
                    {
                        "id": 131734505,
                        "name": "Identifiant",
                        "value": f"{user_id}",
                        "inline": True
                    },
                    {
                        "id": 803754614,
                        "name": "Organisation",
                        "value": f"{organization_id}",
                        "inline": True
                    }
                ],
                "title": "🙋‍♂️ Un nouvel utilisateur a été crée sur le SSO",
                "footer": {
                    "text": "nyx@rezoleo.fr"
                },
                "color": 15601
            }
        ]
    }

    async with httpx.AsyncClient() as client:
        await client.post(DISCORD_WEBHOOK_URL, json=message)

    return {"status": "ok"}


@app.post("/on-user-updated")
async def update_user(payload: dict[str, Any]):
    logging.info(f"User updated: {payload}")

    # a user cannot change their own username
    if payload["userID"] == payload["request"]["userId"] and "username" in payload["request"]:
        raise HTTPException(status_code=403, detail="Username change not allowed")

    return {"status": "ok"}


@app.post("/on-userinfo")
async def userinfo(payload: dict[str, Any]):
    logging.debug(f"Userinfo requested: {payload}")

    # add roles to the userinfo claims based on user grants
    # each grant becomes a claim "roles-<project_name>" with the list of roles
    # e.g. "roles-REZOLEO": ["admin", "rezoleo"]
    append_claims = [
        {"key": f"roles-{grant['project_name']}", "value": grant["roles"]}
        for grant in payload.get("user_grants", [])
    ]

    return {"append_claims": append_claims}
