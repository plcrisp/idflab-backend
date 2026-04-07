import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

if TYPE_CHECKING:
    from .project import Project
    from .idf_value import IdfValue

from ..db.base import Base
from .enums import DistributionEnum

class IdfResult(Base):
    __tablename__ = "idf_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    distribution: Mapped[DistributionEnum] = mapped_column(nullable=False)
    best_sse: Mapped[float] = mapped_column(Float, nullable=False)
    idf_params: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    project: Mapped["Project"] = relationship(back_populates="idf_results")
    idf_values: Mapped[list["IdfValue"]] = relationship(back_populates="idf_result")