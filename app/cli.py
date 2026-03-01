"""Flask CLI commands for seeding the database."""

import click
from flask.cli import with_appcontext

from app.extensions import db
from app.models.user import User
from app.helper import logger as app_logger


SEED_USERS = [
    {
        "name": "Admin User",
        "email": "admin@mail.com",
        "role": "admin",
        "oauth_provider": None,
        "oauth_id": None,
        "profile_picture": None,
    },
    # {
    #     "name": "John Doe",
    #     "email": "john@example.com",
    #     "role": "user",
    #     "oauth_provider": None,
    #     "oauth_id": None,
    #     "profile_picture": None,
    # },
    # {
    #     "name": "Jane Smith",
    #     "email": "jane@example.com",
    #     "role": "user",
    #     "oauth_provider": None,
    #     "oauth_id": None,
    #     "profile_picture": None,
    # },
]


@click.command("seed-users")
@click.option(
    "--force", is_flag=True, help="Drop existing seed users and re-create them."
)
@with_appcontext
def seed_users(force):
    """Seed the database with default users."""
    created = 0
    skipped = 0

    for user_data in SEED_USERS:
        existing = User.query.filter_by(email=user_data["email"]).first()

        if existing:
            if force:
                db.session.delete(existing)
                db.session.flush()
                app_logger.json_logger.info(
                    f"Deleted existing user: {user_data['email']}"
                )
            else:
                click.echo(f"  ⏭  Skipped (exists): {user_data['email']}")
                skipped += 1
                continue

        user = User(**user_data)
        db.session.add(user)
        db.session.flush()
        click.echo(
            f"  ✅ Created: {user_data['email']} (role={user_data['role']}, id={user.id})"
        )
        created += 1

    db.session.commit()
    click.echo(f"\nDone! Created: {created}, Skipped: {skipped}")


def register_cli(app):
    """Register all CLI commands with the Flask app."""
    app.cli.add_command(seed_users)
