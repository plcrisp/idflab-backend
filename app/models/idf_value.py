import uuid
from typing import TYPE_CHECKING
from sqlalchemy import Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from ..db.base import Base

if TYPE_CHECKING:
    from .idf_result import IdfResult

class IdfValue(Base):
    __tablename__ = "idf_values"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    idf_result_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("idf_results.id"), nullable=False)
    duration: Mapped[float] = mapped_column(Float, nullable=False)
    return_period: Mapped[float] = mapped_column(Float, nullable=False)
    intensity: Mapped[float] = mapped_column(Float, nullable=False)

    idf_result: Mapped["IdfResult"] = relationship(back_populates="idf_values")