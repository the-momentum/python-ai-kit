from typing import Any
from fastapi import Request
from sqladmin import ModelView
from pydantic import BaseModel
from sqladmin.models import ModelViewMeta

from app.database import BaseDbModel

_CONFIG_TYPE = dict[str, str | list[str] | None]

class BaseAdminMeta(ModelViewMeta):
    def __new__(mcls, name: str, bases: tuple, attrs: dict, **kwargs: Any) -> ModelViewMeta:
        cls = super().__new__(mcls, name, bases, attrs, **kwargs)

        if 'create_schema' in kwargs:
            cls._create_schema = kwargs['create_schema']
        if 'update_schema' in kwargs:
            cls._update_schema = kwargs['update_schema']

        if auto_exclude_fields := mcls._get_fields_with_default_factory(cls):
            cls.form_excluded_columns = auto_exclude_fields

        return cls

    @staticmethod
    def _get_fields_with_default_factory(cls) -> list[str]:
        """Get fields with default_factory from schemas."""
        exclude_fields = []
        
        for schema_attr in ['_create_schema', '_update_schema']:
            if schema := getattr(cls, schema_attr, None):
                for field_name, field_info in schema.model_fields.items():
                    if getattr(field_info, 'default_factory', None):
                        exclude_fields.append(field_name)
        
        return list(set(exclude_fields))


class BaseAdminView(ModelView, metaclass=BaseAdminMeta):
    _create_schema: type[BaseModel]
    _update_schema: type[BaseModel]
    
    column_list: str | list[str] = "__all__"
    column_exclude_list: list[str] = []
    # column_searchable_list: list[str] = []
    # column_sortable_list: list[str] = []

    form_excluded_columns: list[str] = []
    # form_create_rules: list[str] = []
    # form_edit_rules: list[str] = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
    
    async def on_model_change(
        self, 
        data: dict[str, Any], 
        model: BaseDbModel, 
        is_created: bool, 
        request: Request
    ) -> None:
        schema = self._create_schema if is_created else self._update_schema
        validated_data = schema.model_validate(data)
        
        update_dict = validated_data.model_dump(exclude_none=True)
        
        for field_name, field_value in update_dict.items():
            setattr(model, field_name, field_value)