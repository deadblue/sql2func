__author__ = 'deadblue'

from typing import Type

try:
    from pydantic import BaseModel
    
    def is_pydantic_model(cls: Type) -> bool:
        return issubclass(cls, BaseModel)
except: 
    def is_pydantic_model(cls: Type) -> bool:
        return False
