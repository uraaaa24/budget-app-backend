from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.category.category_entity import Category


class GetCategoryResponseSchema(BaseModel):
    """Schema for a category in response."""

    id: UUID | str = Field(..., description="Unique identifier of the category")
    user_id: str | None = Field(
        None, description="Identifier of the user who owns the category", exclude=True
    )
    name: str = Field(..., description="Name of the category")
    description: str = Field("", description="Description of the category")
    type: str = Field(..., description="Type of the category (income or expense)")
    is_archived: bool = Field(
        ..., description="Indicates if the category is archived", exclude=True
    )
    created_at: str = Field(
        ..., description="Timestamp when the category was created", exclude=True
    )
    updated_at: str = Field(
        ..., description="Timestamp when the category was last updated", exclude=True
    )

    @staticmethod
    def from_entity(entity: Category) -> "GetCategoryResponseSchema":
        """Convert a Category entity to response schema."""
        return GetCategoryResponseSchema(
            id=entity.id,
            user_id=entity.user_id,
            name=entity.name.value,
            description=entity.description,
            type=str(entity.type.value),
            is_archived=entity.is_archived,
            created_at=entity.created_at.isoformat(),
            updated_at=entity.updated_at.isoformat(),
        )


class GetCategoryListResponseSchema(BaseModel):
    """Schema for list of categories in response."""

    categories: list[GetCategoryResponseSchema] = Field(..., description="List of categories")

    @staticmethod
    def from_entities(entities: list[Category]) -> "GetCategoryListResponseSchema":
        """Convert a list of Category entities to response schema."""
        return GetCategoryListResponseSchema(
            categories=[GetCategoryResponseSchema.from_entity(entity) for entity in entities]
        )
