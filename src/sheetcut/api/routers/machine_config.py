from __future__ import annotations

from fastapi import APIRouter

from sheetcut.api.deps import SessionDep, UserDep
from sheetcut.api.schemas import MachineConfigIn, MachineConfigOut
from sheetcut.core import MachineConfig
from sheetcut.services import MachineConfigService

router = APIRouter(prefix="/machine-config", tags=["machine-config"])


@router.get("")
def get_current(session: SessionDep, _user: UserDep) -> MachineConfigOut:
    return MachineConfigOut.from_row(MachineConfigService(session).current_row())


@router.put("")
def update(body: MachineConfigIn, session: SessionDep, _user: UserDep) -> MachineConfigOut:
    config = MachineConfig(**body.model_dump(exclude={"comment"}))
    return MachineConfigOut.from_row(MachineConfigService(session).update(config, body.comment))


@router.get("/history")
def history(session: SessionDep, _user: UserDep) -> list[MachineConfigOut]:
    return [MachineConfigOut.from_row(r) for r in MachineConfigService(session).history()]
