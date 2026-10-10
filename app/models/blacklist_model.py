from sqlalchemy.orm import Mapped, mapped_column 

from datetime import datetime

from app.core.database import Base


class BlackList(Base):
   __tablename__ = "black_tokens"
   
   id: Mapped[int] = mapped_column(primary_key=True)
   token: Mapped[str] = mapped_column(unique=True, index=True)
   adding_date: Mapped[datetime] = mapped_column(default=datetime.utcnow)

