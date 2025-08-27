import base64

import httpx

from .zitadel_schemas import *


class ZitadelConflict(Exception):
    pass


def _user_exists(resp: httpx.Response) -> bool:
    if resp.status_code == 401:
        raise RuntimeError("Zitadel auth failed – PAT invalide ou scope insuffisant")
    resp.raise_for_status()
    users = resp.json().get("result", [])
    return len(users) > 0


class ZitadelClient:
    def __init__(self, base_url: str, pat: str, organization_id: str):
        if not base_url:
            raise RuntimeError("ZITADEL_BASE_URL manquant (variable d'environnement)")
        if not pat:
            raise RuntimeError("ZITADEL_PAT manquant (variable d'environnement)")
        if not organization_id:
            raise RuntimeError("ZITADEL_ORGANIZATION_ID manquant (variable d'environnement)")

        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(
            headers={
                "Authorization": f"Bearer {pat}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            timeout=30.0
        )
        self.organization_id = organization_id

    def email_exists(self, email: str) -> bool:
        url = f"{self.base_url}/v2/users"
        query = Query(emailQuery=EmailQuery(emailAddress=email))
        body = UserSearchRequest(queries=[query]).model_dump(mode="json", exclude_none=True)
        resp = self.client.post(url, json=body)
        return _user_exists(resp)

    def username_exists(self, username: str) -> bool:
        url = f"{self.base_url}/v2/users"
        query = Query(userNameQuery=UsernameQuery(userName=username))
        body = UserSearchRequest(queries=[query]).model_dump(mode="json", exclude_none=True)
        resp = self.client.post(url, json=body)
        return _user_exists(resp)

    def ensure_unique_username(self, base: str) -> str:
        candidate = base
        i = 2
        while self.username_exists(candidate):
            candidate = f"{base}{i}"
            i += 1
        return candidate

    def create_human_user(self, username: str, email: str, given_name: str, family_name: str) -> str:
        url = f"{self.base_url}/v2/users/human"
        body = UserCreateRequest(
            organizationId=self.organization_id,
            username=username,
            profile=UserProfile(
                givenName=given_name,
                familyName=family_name,
                displayName=f"{given_name} {family_name}",
                # preferredLanguage="fr",
            ),
            email=UserEmail(email=email)
        ).model_dump(mode="json", exclude_none=True)
        resp = self.client.post(url, json=body)
        if resp.status_code == 409:
            raise ZitadelConflict()
        if resp.status_code == 401:
            raise RuntimeError("Zitadel auth failed – PAT invalide ou scope insuffisant")
        resp.raise_for_status()
        data = resp.json()
        return data.get("userId") or data.get("user_id") or data.get("id")

    def set_user_metadata(self, user_id: str, kv: dict[str, str]):
        url = f"{self.base_url}/v2/users/{user_id}/metadata"
        # For HTTP requests, values must be base64 encoded.
        meta_list = [MetadataEntry(key=k, value=base64.b64encode(v.encode()).decode()) for k, v in kv.items()]
        body = Metadata(metadata=meta_list).model_dump(mode="json", exclude_none=True)
        resp = self.client.post(url, json=body)
        resp.raise_for_status()
