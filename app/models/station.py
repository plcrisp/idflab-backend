import uuid
from datetime import date
from typing import TYPE_CHECKING
from sqlalchemy import String, Float, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

if TYPE_CHECKING:
    from app.models.precipitation_data import PrecipitationData
    from app.models.project import Project

from ..db.base import Base
from .enums import SourceEnum, StationTypeEnum

class Station(Base):
    __tablename__ = "stations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String, nullable=False)
    source: Mapped[SourceEnum] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    city: Mapped[str | None] = mapped_column(String, nullable=True)
    state: Mapped[str | None] = mapped_column(String, nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str | None] = mapped_column(String, nullable=True) 
    operation_start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    last_data_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    station_type: Mapped[StationTypeEnum] = mapped_column(String, nullable=False)

    precipitation_data: Mapped[list["PrecipitationData"]] = relationship(back_populates="station")
    projects: Mapped[list["Project"]] = relationship(back_populates="station")