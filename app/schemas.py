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

    
class GenealogieCheval(BaseModel):
    nom: str
    sexe: Optional[str]
    couleur: Optional[str]
    dateDeNaissance: Optional[int]
    naisseur: Optional[str]
    lienIfce: Optional[str]
    pere: Optional['GenealogieCheval']
    mere: Optional['GenealogieCheval']

class GenealogieResponse(BaseModel):
    nomCheval: str
    sexeCheval: str
    couleurCheval: str
    dateDeNaissance: int
    naisseur: str
    lienIfce: str
    pere: Optional[GenealogieCheval]
    mere: Optional[GenealogieCheval]

GenealogieResponse.model_rebuild()
GenealogieCheval.model_rebuild()