import logging
import os
from typing import Any

import httpx
from fastapi import FastAPI

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
