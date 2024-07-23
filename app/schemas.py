# schemas.py
from pydantic import BaseModel

class ChevalResponse(BaseModel):
    nomCheval: str
    nombreCoursesEnregistrer: int
    nombreCoursesTotal: int
    precisionPercent: float

