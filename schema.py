from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class InfoSchema(BaseModel):
    country: str
    duration: str
    style: str 
    
    class Config:
        orm_mode = True

