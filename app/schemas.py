# schemas.py
from pydantic import BaseModel
from typing import Optional

class ChevalResponse(BaseModel):
    nomCheval: str
    nombreCoursesEnregistrer: int
    nombreCoursesTotal: int
    precisionPercent: float
    vitesseMoyenneKmh: float
    nombrePremier: int
    nombreDeuxieme: int
    nombreTroisieme: int
    nombreQuatrieme: int 
    nombreCinquieme: int
    nombreDisqualifications: int
    placeMoyenne: float
    montantTotalGagne: int

class StatsIfceResponse(BaseModel):
    dispoIFCE: str
    lienIfce: str
    dispoStats: str
    race: str

class InfosResponse(BaseModel):
    nom: str
    sexe: str
    couleur: str
    dateDeNaissance: Optional[int] = None
    naisseur: Optional[str] = None
    lienIfce: Optional[str] = None
    pere: str
    mere: str

class GenealogieResponse(BaseModel):
    nom: str
    sexe: str
    couleur: str
    dateDeNaissance: Optional[int] = None
    naisseur: Optional[str] = None
    lienIfce: Optional[str] = None
    pere: str
    informationsPere: Optional['GenealogieResponse'] = None
    mere: str
    informationsMere: Optional['GenealogieResponse'] = None

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True