from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from app.database import engine, Base
from app.crud import create_test_entities
import logging

revision = "create_test_entities"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind()
    Base.metadata.create_all(bind)
    
    session = sessionmaker(bind=bind)
    
    with session() as db:
        try:
            create_test_entities(db)
            logging.warning("Тестовые пользователи успешно созданы.")
        except Exception as e:
            logging.warning(f"Произошла ошибка: {e}")
            logging.exception("Ошибка при создании тестовых пользователей")

def downgrade():
    pass