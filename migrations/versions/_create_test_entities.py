from alembic import op
import sqlalchemy as sa
from datetime import datetime

from app.security import hash_password

revision = "xxxxxxxxxxxx"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    conn = op.get_bind()

    test_password_hash = hash_password("123")

    conn.execute(
        sa.text("""
            INSERT INTO users (id, email, full_name, password_hash, is_admin)
            VALUES (:id, :email, :full_name, :password_hash, :is_admin)
            ON CONFLICT (id) DO NOTHING
        """),
        [
            {"id": 1000, "email": "test_user@example.com", "full_name": "Иван Иваныч",
             "password_hash": test_password_hash, "is_admin": False},
            {"id": 1001, "email": "test_admin@example.com", "full_name": "Дима Админ",
             "password_hash": test_password_hash, "is_admin": True}
        ]
    )

    conn.execute(
        sa.text("""
            INSERT INTO accounts (id, user_id, balance)
            VALUES (:id, :user_id, :balance)
            ON CONFLICT (id) DO NOTHING
        """),
        {"id": 2000, "user_id": 1000, "balance": 0}
    )

def downgrade():
    conn = op.get_bind()
    conn.execute(sa.text("DELETE FROM accounts WHERE id = :id"), {"id": 2000})
    conn.execute(sa.text("DELETE FROM users WHERE id IN (:u1, :u2)"), {"u1": 1000, "u2": 1001})