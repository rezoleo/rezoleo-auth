from typing import Literal

from pydantic import BaseModel, Field


class QueryMeta(BaseModel):
    offset: int = Field(default=0)
    limit: int = Field(default=100)
    asc: bool = Field(default=True)


class EmailQuery(BaseModel):
    emailAddress: str
    method: Literal["TEXT_QUERY_METHOD_EQUALS", "TEXT_QUERY_METHOD_CONTAINS"] = "TEXT_QUERY_METHOD_EQUALS"


class UsernameQuery(BaseModel):
    userName: str
    method: Literal["TEXT_QUERY_METHOD_EQUALS", "TEXT_QUERY_METHOD_CONTAINS"] = "TEXT_QUERY_METHOD_EQUALS"


class Query(BaseModel):
    emailQuery: EmailQuery | None = None
    userNameQuery: UsernameQuery | None = None


class UserSearchRequest(BaseModel):
    query: QueryMeta = Field(default_factory=QueryMeta)
    sortingColumn: str = "USER_FIELD_NAME_UNSPECIFIED"
    queries: list[Query]


class UserProfile(BaseModel):
    givenName: str
    familyName: str
    displayName: str
    preferredLanguage: str | None = None


class UserEmail(BaseModel):
    email: str
    isVerified: bool | None = None


class MetadataEntry(BaseModel):
    key: str
    value: str


class HumanCreateRequest(BaseModel):
    profile: UserProfile
    email: UserEmail
    metadata: list[MetadataEntry]


class UserCreateRequest(BaseModel):
    organizationId: str
    username: str
    human: HumanCreateRequest
