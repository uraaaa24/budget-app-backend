from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4


@dataclass(eq=False, slots=True)
class BaseEntity:
    """Base class for all domain entities."""

    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self):
        """Ensure created_at and updated_at are set correctly."""
        self.updated_at = max(self.updated_at, self.created_at)

    def __eq__(self, obj: object) -> bool:
        """Entities are equal if they have the same ID and are of the same type."""
        if not isinstance(obj, self.__class__):
            return False
        return self.id == obj.id

    def __hash__(self) -> int:
        """Hash based on the entity's ID."""
        return hash((type(self), self.id))

    def touch(self) -> None:
        """Update the updated_at timestamp to the current time."""
        self.updated_at = datetime.now(UTC)
