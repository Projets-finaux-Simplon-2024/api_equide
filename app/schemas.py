from pydantic import BaseModel
from typing import List, Optional
from datetime import date, time

# Schéma pour la requête contenant le nom du cheval
class ChevalRequest(BaseModel):
    nom_tf: str

# Modèle pour ChevauxTrotteurFrancais
class ChevalBase(BaseModel):
    nom_tf: str
    sexe_tf: str
    couleur_tf: Optional[str]
    annee_naissance_tf: int
    pere_tf: Optional[str]
    mere_tf: Optional[str]
    date_decee_tf: Optional[date]
    naisseur_tf: Optional[str]
    lien_ifce_tf: Optional[str]

class ChevalCreate(ChevalBase):
    pass

class Cheval(ChevalBase):
    id_tf: int

    class Config:
        orm_mode = True

# Modèle pour ParticipationsAuxCourses
class ParticipationBase(BaseModel):
    id_course: int
    nom: str
    numero_cheval: Optional[int]
    age: Optional[int]
    sexe: Optional[str]
    race: Optional[str]
    statut_au_depart: Optional[str]
    proprietaire: Optional[str]
    entraineur: Optional[str]
    driver: Optional[str]
    driverChange: Optional[bool]
    code_robe: Optional[str]
    libelle_court_robe: Optional[str]
    libelle_long_robe: Optional[str]
    nombre_courses: Optional[int]
    nombre_victoires: Optional[int]
    nombre_places: Optional[int]
    nom_pere: Optional[str]
    nom_mere: Optional[str]
    place_dans_la_course: Optional[int]
    jument_pleine: Optional[bool]
    engagement: Optional[bool]
    supplement: Optional[int]
    handicap_distance: Optional[int]
    poids_condition_monte_change: Optional[bool]
    temps_obtenu: Optional[int]
    temps_obtenu_en_minute: Optional[str]
    reduction_kilometrique: Optional[int]
    allure: Optional[str]

class ParticipationCreate(ParticipationBase):
    pass

class Participation(ParticipationBase):
    id_participation: int

    class Config:
        orm_mode = True

# Modèle pour le retour des données de course d'un cheval
class ChevalWithParticipations(Cheval):
    participations: List[Participation] = []

# Modèle pour la généalogie d'un cheval
class Genealogy(BaseModel):
    cheval: Cheval
    pere: Optional['Genealogy']
    mere: Optional['Genealogy']

    class Config:
        orm_mode = True
