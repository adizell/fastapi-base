"""
Base CRUD Module

This module defines a generic base CRUD class with common database operations.
"""
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import Select

from app.db.base import Base

# Define generic types for models and schemas
ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Generic CRUD operations for SQLAlchemy models.

    Attributes:
        model: SQLAlchemy model class
    """

    def __init__(self, model: Type[ModelType]):
        """
        Initialize with SQLAlchemy model class.

        Args:
            model: SQLAlchemy model class
        """
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        """
        Get a single record by ID.

        Args:
            db: Database session
            id: Record ID

        Returns:
            Optional[ModelType]: Found record or None
        """
        query = select(self.model).where(self.model.id == id)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[List[Any]] = None,
    ) -> List[ModelType]:
        """
        Get multiple records with pagination and optional filters.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Optional list of filter conditions

        Returns:
            List[ModelType]: List of records
        """
        query = select(self.model)

        if filters:
            query = query.where(and_(*filters))

        query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        return result.scalars().all()

    async def get_count(
        self,
        db: AsyncSession,
        filters: Optional[List[Any]] = None,
    ) -> int:
        """
        Get count of records with optional filters.

        Args:
            db: Database session
            filters: Optional list of filter conditions

        Returns:
            int: Count of records
        """
        query = select(func.count()).select_from(self.model)

        if filters:
            query = query.where(and_(*filters))

        result = await db.execute(query)
        return result.scalar() or 0

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new record.

        Args:
            db: Database session
            obj_in: Create schema with record data

        Returns:
            ModelType: Created record
        """
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        """
        Update a record.

        Args:
            db: Database session
            db_obj: Existing database object
            obj_in: Update schema or dict with fields to update

        Returns:
            ModelType: Updated record
        """
        obj_data = jsonable_encoder(db_obj)

        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: Any) -> Optional[ModelType]:
        """
        Delete a record by ID.

        Args:
            db: Database session
            id: Record ID

        Returns:
            Optional[ModelType]: Deleted record or None
        """
        obj = await self.get(db, id)
        if obj:
            await db.delete(obj)
            await db.flush()
        return obj

    def get_search_query(
        self,
        query: Select,
        search_term: Optional[str],
        search_fields: List[Any],
    ) -> Select:
        """
        Add search conditions to query.

        Args:
            query: Existing query
            search_term: Search term
            search_fields: Fields to search in

        Returns:
            Select: Query with search conditions added
        """
        if not search_term or not search_fields:
            return query

        # Create OR conditions for each search field
        search_conditions = []
        for field in search_fields:
            search_conditions.append(field.ilike(f"%{search_term}%"))

        return query.where(or_(*search_conditions))
