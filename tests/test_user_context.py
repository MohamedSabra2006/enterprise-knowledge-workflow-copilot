from app.db.session import SessionLocal
from app.auth.user_context import load_user_context, UserNotFoundError

with SessionLocal() as db:
    for uid in (1, 2, 3):
        ctx = load_user_context(db, uid)
        print(
            ctx.display_name, ctx.role,
            "| member:", sorted(ctx.member_team_ids),
            "| managed:", sorted(ctx.managed_team_ids),
            "| accessible:", sorted(ctx.accessible_team_ids),
            "| grants:", ctx.granted_sources,
        )

    try:
        load_user_context(db, 999)
    except UserNotFoundError as e:
        print("OK, unknown user rejected:", e)