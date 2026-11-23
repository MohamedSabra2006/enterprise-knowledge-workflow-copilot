from sqlalchemy import select
from sqlalchemy.orm import configure_mappers

import app.models  # noqa: F401  (registers every model)
from app.db.session import SessionLocal
from app.models import AppUser, UserTeam

configure_mappers()  # raises if any relationship is broken

with SessionLocal() as db:
    users = db.scalars(select(AppUser)).all()
    for u in users:
        teams = [(ut.team.team_name, ut.is_manager) for ut in u.user_teams]
        print(u.display_name, u.role_name, u.organization.organization_name, teams)