from typing import TypeVar, Generic, Optional, List
from beanie import Document
from pydantic import BaseModel

ModelType = TypeVar('ModelType', bound=Document)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)

class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: ModelType):
        self.model = model

    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        obj = self.model(**obj_in.dict())
        await obj.insert()
        return obj

    async def get(self, id: str) -> Optional[ModelType]:
        return await self.model.get(id)

    async def update(self, id: str, obj_in: UpdateSchemaType) -> Optional[ModelType]:
        obj = await self.get(id)
        if not obj:
            return None
        for field, value in obj_in.dict(exclude_unset=True).items():
            setattr(obj, field, value)
        await obj.save()
        return obj

    async def delete(self, id: str) -> Optional[ModelType]:
        obj = await self.get(id)
        if not obj:
            return None
        await obj.delete()
        return obj

    async def list(self) -> List[ModelType]:
        return await self.model.find_all().to_list()