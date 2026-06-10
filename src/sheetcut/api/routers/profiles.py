from __future__ import annotations

from fastapi import APIRouter

from sheetcut.api.deps import ArtifactsDep, SessionDep, UserDep
from sheetcut.api.schemas import GenerateIn, GenerationSummary, ProfileIn, ProfileOut
from sheetcut.services import GenerationService, ProfileService

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.get("")
def list_profiles(session: SessionDep, _user: UserDep) -> list[ProfileOut]:
    return [ProfileOut.from_row(r) for r in ProfileService(session).list_all()]


@router.post("", status_code=201)
def create_profile(body: ProfileIn, session: SessionDep, _user: UserDep) -> ProfileOut:
    return ProfileOut.from_row(ProfileService(session).create(body.name, body.tools))


@router.get("/{profile_id}")
def get_profile(profile_id: int, session: SessionDep, _user: UserDep) -> ProfileOut:
    return ProfileOut.from_row(ProfileService(session).get(profile_id))


@router.put("/{profile_id}")
def update_profile(
    profile_id: int, body: ProfileIn, session: SessionDep, _user: UserDep
) -> ProfileOut:
    return ProfileOut.from_row(ProfileService(session).update(profile_id, body.name, body.tools))


@router.delete("/{profile_id}", status_code=204)
def delete_profile(profile_id: int, session: SessionDep, _user: UserDep) -> None:
    ProfileService(session).delete(profile_id)


@router.post("/{profile_id}/generate", status_code=201)
def generate(
    profile_id: int,
    body: GenerateIn,
    session: SessionDep,
    artifacts: ArtifactsDep,
    _user: UserDep,
) -> GenerationSummary:
    row = GenerationService(session, artifacts).generate_for_profile(profile_id, body)
    return GenerationSummary.from_row(row)
