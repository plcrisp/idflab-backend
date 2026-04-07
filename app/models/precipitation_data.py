import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

if TYPE_CHECKING:
    from app.models.station import Station

from ..db.base import Base

class PrecipitationData(Base):
    __tablename__ = "precipitation_data"

    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    station_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("stations.id"), primary_key=True)
    precipitation_mm: Mapped[float] = mapped_column(Float, nullable=False)
    filled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relacionamentos
    station: Mapped["Station"] = relationship(back_populates="precipitation_data")