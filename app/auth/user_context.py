from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import PurePath

from sqlalchemy import or_, select, true
from sqlalchemy.orm import Session

from app.models import AppUser, DocumentUserGrant, KnowledgeDocument, Team, UserTeam


class UserNotFoundError(Exception):
    """User does not exist or is inactive."""


@dataclass(frozen=True)
class UserContext:
    user_id: int
    organization_id: int
    display_name: str
    email: str
    role: str
    # Teams the user belongs to.
    member_team_ids: frozenset[int]
    # Teams the user manages (IsManager = 1).
    managed_team_ids: frozenset[int]
    # Teams whose business data the user may query (derived from role).
    accessible_team_ids: frozenset[int]
    # Documents granted to this user individually and not expired.
    granted_document_ids: frozenset[str]
    granted_sources: tuple[str, ...]

    @property
    def is_ceo(self) -> bool:
        return self.role == "ceo"

    @property
    def is_manager(self) -> bool:
        return self.role == "manager"


def load_user_context(db: Session, user_id: int) -> UserContext:
    user = db.get(AppUser, user_id)

    if user is None or not user.is_active:
        raise UserNotFoundError(f"No active user with id {user_id}")

    role = user.role_name.strip().lower()

    memberships = db.execute(
        select(UserTeam.team_id, UserTeam.is_manager)
        .join(Team, Team.team_id == UserTeam.team_id)
        .where(
            UserTeam.user_id == user.user_id,
            Team.organization_id == user.organization_id,  # org isolation
        )
    ).all()

    member_team_ids = frozenset(team_id for team_id, _ in memberships)
    managed_team_ids = frozenset(team_id for team_id, is_mgr in memberships if is_mgr)

    # Team scope is derived from the role, not stored on the user.
    if role == "ceo":
        accessible = frozenset(
            db.scalars(
                select(Team.team_id).where(Team.organization_id == user.organization_id)
            ).all()
        )
    elif role == "manager":
        accessible = managed_team_ids
    else:
        accessible = member_team_ids

    # Individual document grants: not expired, document active, same organization.
    now = datetime.now(timezone.utc).replace(tzinfo=None)  # DATETIME2 holds UTC

    grants = db.execute(
        select(KnowledgeDocument.document_id, KnowledgeDocument.source_path)
        .join(DocumentUserGrant, DocumentUserGrant.document_id == KnowledgeDocument.document_id)
        .where(
            DocumentUserGrant.user_id == user.user_id,
            KnowledgeDocument.organization_id == user.organization_id,
            KnowledgeDocument.is_active == true(),
            or_(DocumentUserGrant.expires_at.is_(None), DocumentUserGrant.expires_at > now),
        )
    ).all()

    return UserContext(
        user_id=user.user_id,
        organization_id=user.organization_id,
        display_name=user.display_name,
        email=user.email,
        role=role,
        member_team_ids=member_team_ids,
        managed_team_ids=managed_team_ids,
        accessible_team_ids=accessible,
        granted_document_ids=frozenset(str(doc_id) for doc_id, _ in grants),
        # Current retrieval filters by file name; Step 4 switches this to document_id.
        granted_sources=tuple(PurePath(path).name for _, path in grants),
    )