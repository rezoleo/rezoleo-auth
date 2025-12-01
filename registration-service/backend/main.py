import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .utils import (
    parse_school_email,
    titlecase_name,
    sanitize_username_base,
)
from .zitadel_client import ZitadelClient, ZitadelConflict


class RegisterRequest(BaseModel):
    email: str
    first_name: str
    last_name: str


class RegisterResponse(BaseModel):
    user_id: str
    username: str
    email: str
    first_name: str
    last_name: str
    school: str


app = FastAPI(title="registration-service")

# CORS for local dev/front hosting
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

zitadel = ZitadelClient(
    base_url=os.getenv("ZITADEL_BASE_URL"),
    pat=os.getenv("ZITADEL_PAT"),
    organization_id=os.getenv("ZITADEL_ORGANIZATION_ID")
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/register", response_model=RegisterResponse)
def register(req: RegisterRequest):
    # 1) Validate email and extract parts
    try:
        first, last, school = parse_school_email(req.email)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if zitadel.email_exists(req.email):
        raise HTTPException(status_code=409,
                            detail="Le compte associé à cet email existe déjà. Contactez Rézoléo si vous pensez qu'il s'agit d'une erreur.")

    # 2) Capitalize names (Jean-paul -> Jean-Paul)
    first_title = titlecase_name(req.first_name)
    last_title = titlecase_name(req.last_name)

    # 3) Generate username base: firstname-lastname
    username_base = sanitize_username_base(first, last)

    # 4) Ensure uniqueness by checking Zitadel list users
    username = zitadel.ensure_unique_username(username_base)

    # 5) Create user in Zitadel
    try:
        user_id = zitadel.create_human_user(
            username=username,
            email=req.email,
            given_name=first_title,
            family_name=last_title,
            school=school.lower(),
        )
    except ZitadelConflict:
        raise HTTPException(status_code=409, detail="Une erreur est survenue. Merci de réessayer.")

    return RegisterResponse(
        user_id=user_id,
        username=username,
        email=req.email,
        first_name=first_title,
        last_name=last_title,
        school=school.lower(),
    )


# Serve the static frontend
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="static")
