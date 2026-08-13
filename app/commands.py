import click

from app.extensions import db
from app.models import User
from app.utils.security import hash_password


def register_commands(app):

    @app.cli.command("create-admin")
    @click.option("--name", prompt="Admin name")
    @click.option("--email", prompt="Admin email")
    @click.option(
        "--password",
        prompt="Admin password",
        hide_input=True,
        confirmation_prompt=True
    )
    def create_admin(name, email, password):

        email = email.lower().strip()

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            click.echo("A user with that email already exists.")
            return

        admin = User(
            name=name,
            email=email,
            password_hash=hash_password(password),
            role="admin"
        )

        db.session.add(admin)
        db.session.commit()

        click.echo(f"Admin account created: {email}")