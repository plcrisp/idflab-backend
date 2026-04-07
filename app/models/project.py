import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

if TYPE_CHECKING:
    from app.models.idf_result import IdfResult
    from app.models.job import Job
    from app.models.station import Station
    from app.models.user import User

from ..db.base import Base
from .enums import ScenarioEnum, BiasCorrectionEnum, DisaggregationEnum

class Project(Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    station_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("stations.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    scenario: Mapped[ScenarioEnum] = mapped_column(nullable=False)
    bias_correction: Mapped[BiasCorrectionEnum] = mapped_column(nullable=False)
    disaggregation: Mapped[DisaggregationEnum] = mapped_column(nullable=False)
    climbra_file_s3: Mapped[str | None] = mapped_column(String, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user: Mapped["User"] = relationship(back_populates="projects")
    station: Mapped["Station"] = relationship(back_populates="projects")
    jobs: Mapped[list["Job"]] = relationship(back_populates="project")
    idf_results: Mapped[list["IdfResult"]] = relationship(back_populates="project")