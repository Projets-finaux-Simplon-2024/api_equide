# schemas.py
from pydantic import BaseModel
from typing import Optional, List, Any

# ---- Endpoint stats-ifce
class StatsIfceResponse(BaseModel):
    dispoIFCE: str
    lienIfce: str
    dispoStats: str
    race: str




# ---- Reponse de base
class InfosResponse(BaseModel):
    id: int
    nom: str
    sexe: str
    couleur: str
    dateDeNaissance: Optional[int] = None
    naisseur: Optional[str] = None
    lienIfce: Optional[str] = None
    pere: str
    mere: str

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=obj.id_tf,
            nom=obj.nom_tf,
            sexe=obj.sexe_tf,
            couleur=obj.couleur_tf,
            dateDeNaissance=obj.annee_naissance_tf,
            naisseur=obj.naisseur_tf,
            lienIfce=obj.lien_ifce_tf,
            pere=obj.pere_tf,
            mere=obj.mere_tf,
        )



# ---- Endpoint pagination
class PaginationResponse(BaseModel):
    total_results: int
    total_pages: int
    current_page: int
    page_size: int
    results: List[InfosResponse]




# ---- Endpoint stat-cheval
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