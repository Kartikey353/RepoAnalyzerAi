from sqlalchemy import Column, String, Integer, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
import uuid
from core.database import Base


class TaskStatus(enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class TaskResult(Base):
    __tablename__ = "task_results"

    task_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    status = Column(Enum(TaskStatus), nullable=False, default=TaskStatus.pending)
    results = Column(JSON, nullable=True)  # JSON field to store analysis results
    total_files = Column(Integer, nullable=True)
    total_issues = Column(Integer, nullable=True)
    critical_issues = Column(Integer, nullable=True)

    def __repr__(self):
        return f"<TaskResult(task_id={self.task_id}, status={self.status})>"
