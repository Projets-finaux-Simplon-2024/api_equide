from fastapi import FastAPI, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import desc
from . import models, schemas, database
from .auth import get_current_user, auth_router
from typing import List
import pandas as pd

# Créer l'application FastAPI avec des métadonnées personnalisées
app = FastAPI(
    docs_url="/",
    redoc_url="/docs",
    title="API de Gestion des Chevaux",
    description="Cette API permet de gérer les informations et les statistiques des chevaux trotteur français.",
    version="1.0.0",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1}
)

# Monter le routeur d'authentification
app.include_router(auth_router, prefix="/auth", tags=["Author"])

# Configurer le répertoire des templates
templates = Jinja2Templates(directory="templates")

# Dépendance pour obtenir une session de base de données
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Fonction pour convertir le temps en secondes
def convertir_temps_en_secondes(temps):
    if not temps or temps == '0m 0s':
        return None  # Valeur manquante pour les temps non disponibles
    minutes, secondes = map(int, temps[:-1].split('m '))
    return minutes * 60 + secondes


# ------------------------------------------------------ Endpoint pour savoir si un cheval a une généalogie ou des stats -----------------------------------|
@app.get(
    "/stats-ifce/{nomCheval}", 
    response_model=schemas.StatsIfceResponse,
    summary="Permet de savoir si un cheval a des données dans la table IFCE et/ou dans la table des courses PMU",
    description="Récupère quelques informations d'une table ou de l'autre ou des deux suivant ce qui est dispo",
    tags=["Consultation des informations chevaux"]
)
def get_stats_ifce(nomCheval: str, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):


    # Récupération du nom et vérification de l'existence du cheval dans la table trotteur français --------------
    nom_cheval_normalise = nomCheval.upper()
    db_cheval_ifce = db.query(models.ChevauxTrotteurFrancais).filter(models.ChevauxTrotteurFrancais.nom_tf == nom_cheval_normalise).first()
    if db_cheval_ifce is None:
        dispo_ifce = "Non"
        lien_ifce = "Indisponible"
        race = "Le cheval n'est pas un trotteur français"
    else:
        dispo_ifce = "Oui"
        lien_ifce = db_cheval_ifce.lien_ifce_tf
        race = "Le cheval est un trotteur français"

    # Récupération du nom et vérification de l'existence du cheval dans les courses -----------------------------
    db_cheval_stat = db.query(models.ParticipationsAuxCourses).filter(models.ParticipationsAuxCourses.nom == nom_cheval_normalise).order_by(desc(models.ParticipationsAuxCourses.id_participation)).first()
    if db_cheval_stat is None:
        dispo_stats = "Aucune course disponible"
    else:
        nombre_courses_enregistrer = db.query(models.ParticipationsAuxCourses).filter(models.ParticipationsAuxCourses.nom == nom_cheval_normalise).count()
        dispo_stats = f"{nombre_courses_enregistrer} courses sont disponibles"
        race = f"Le cheval est un {db_cheval_stat.race}"

    return schemas.StatsIfceResponse(
            dispoIFCE = dispo_ifce,
            lienIfce = lien_ifce,
            dispoStats = dispo_stats,
            race = race
        )
# ----------------------------------------------------------------------------------------------------------------------------------------------------------|



# ------------------------------------------------------ Endpoint pour récupérer la pagination de la table chevaux trotteur Français -----------------------|
@app.get(
    "/chevaux/",
    response_model=schemas.PaginationResponse,
    summary="Lister les chevaux de race trotteur français avec pagination",
    description="Récupère une liste de chevaux trotteur français avec pagination. Permet de spécifier la page et la taille de page pour naviguer à travers les résultats.",
    tags=["Consultation des informations chevaux"]
)
def get_chevaux(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1), db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    # Calculer l'offset et la limite
    offset = (page - 1) * page_size

    # Requête pour obtenir les résultats paginés avec un ordre spécifique
    chevaux = db.query(models.ChevauxTrotteurFrancais).order_by(models.ChevauxTrotteurFrancais.id_tf).offset(offset).limit(page_size).all()

    # Requête pour obtenir le nombre total de résultats
    total_results = db.query(models.ChevauxTrotteurFrancais).count()

    if not chevaux:
        raise HTTPException(status_code=404, detail="Aucun cheval trouvé")

    total_pages = (total_results + page_size - 1) // page_size  # Calcul du nombre total de pages

    # Convertir les résultats en objets Pydantic
    chevaux_pydantic = [schemas.InfosResponse.from_orm(cheval) for cheval in chevaux]

    return schemas.PaginationResponse(
        total_results=total_results,
        total_pages=total_pages,
        current_page=page,
        page_size=page_size,
        results=chevaux_pydantic
    )
# ----------------------------------------------------------------------------------------------------------------------------------------------------------|



# ------------------------------------------------------ Endpoint pour récupérer les infos d'un cheval -----------------------------------------------------|
def get_complete_info(idCheval: int, db: Session):

    cheval = db.query(models.ChevauxTrotteurFrancais).filter(models.ChevauxTrotteurFrancais.id_tf == idCheval).first()

    return schemas.InfosResponse(
        id = cheval.id_tf,
        nom = cheval.nom_tf,
        sexe = cheval.sexe_tf,
        couleur = cheval.couleur_tf,
        dateDeNaissance = cheval.annee_naissance_tf,
        naisseur = cheval.naisseur_tf,
        lienIfce = cheval.lien_ifce_tf,
        pere = cheval.pere_tf,
        mere=cheval.mere_tf,
    )
@app.get(
    "/infos-cheval/{idCheval}",
    response_model=schemas.InfosResponse,
    summary="Obtenir les informations d'un cheval de la race trotteur français",
    description="Récupère les informations détaillées d'un cheval spécifique en utilisant son identifiant.",
    tags=["Consultation des informations chevaux"]
)
def get_infos_cheval(idCheval: int, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):

    cheval = db.query(models.ChevauxTrotteurFrancais).filter(models.ChevauxTrotteurFrancais.id_tf == idCheval).first()

    if cheval:
        infos = get_complete_info (cheval.id_tf, db)

    if not cheval:
        raise HTTPException(status_code=404, detail=f"Le cheval n'est pas un trotteur français !")

    return infos
# ----------------------------------------------------------------------------------------------------------------------------------------------------------|



# ------------------------------------------------------ Endpoint pour récupérer les stats d'un cheval -----------------------------------------------------|
@app.get(
    "/stat-cheval/{nomCheval}",
    response_model=schemas.ChevalResponse,
    summary="Obtenir les statistiques PMU d'un cheval quand elle sont dispos",
    description="Récupère les statistiques détaillées d'un cheval spécifique, y compris le nombre de courses, la vitesse moyenne, les positions obtenues et les gains totaux.",
    tags=["Consultation des informations chevaux"]
)
def get_stat_cheval_by_name(nomCheval: str, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    # Récupération du nom et vérification de l'existence du cheval dans les courses
    nom_cheval_normalise = nomCheval.upper()
    db_cheval = db.query(models.ParticipationsAuxCourses).filter(models.ParticipationsAuxCourses.nom == nom_cheval_normalise, models.ParticipationsAuxCourses.race == "TROTTEUR FRANCAIS").order_by(desc(models.ParticipationsAuxCourses.id_participation)).first()
    if db_cheval is None:
        raise HTTPException(status_code=404, detail="Le cheval n'a pas de courses enregistrées")

    # Récupération du nombre de course et calcul d'une précision
    nombre_courses_enregistrer = db.query(models.ParticipationsAuxCourses).filter(models.ParticipationsAuxCourses.nom == nom_cheval_normalise).count()
    nombre_courses_total = db_cheval.nombre_courses
    precision = (nombre_courses_enregistrer / nombre_courses_total) * 100 if nombre_courses_total > 0 else 0

    # Récupération des courses du cheval
    query = (db.query(models.Courses, models.ParticipationsAuxCourses)
             .join(models.ParticipationsAuxCourses, models.Courses.id_course == models.ParticipationsAuxCourses.id_course)
             .filter(models.ParticipationsAuxCourses.nom == nom_cheval_normalise, models.ParticipationsAuxCourses.race == "TROTTEUR FRANCAIS"))
    results = query.all()

    # Convertir les résultats de la jointure en DataFrame
    data = []
    for course, participation in results:
        row = {**course.__dict__, **participation.__dict__}
        row.pop('_sa_instance_state', None)  # Retirer l'état de SQLAlchemy
        data.append(row)
    df_courses = pd.DataFrame(data)
    print(df_courses)

    # Calcul de la vitesse moyenne
    df_courses['temps_en_secondes'] = df_courses['temps_obtenu_en_minute'].apply(convertir_temps_en_secondes)
    df_courses['vitesse'] = df_courses['distance'] / df_courses['temps_en_secondes']  # Calculer la vitesse (distance en mètres / temps en secondes) en m/s
    df_courses['vitesse_km_h'] = df_courses['vitesse'] * 3.6  # Convertir la vitesse en km/h (1 m/s = 3.6 km/h)
    moyenne_vitesse = df_courses['vitesse_km_h'].mean()
    if pd.isna(moyenne_vitesse):
        moyenne_vitesse = 0.0
    else:
        moyenne_vitesse = round(moyenne_vitesse, 2)  # Calculer la moyenne des vitesses en km/h

    # Calculer le nombre de fois où le cheval est premier, deuxième, etc
    nombre_premier = df_courses[df_courses['place_dans_la_course'] == 1].shape[0]
    nombre_deuxieme = df_courses[df_courses['place_dans_la_course'] == 2].shape[0]
    nombre_troisieme = df_courses[df_courses['place_dans_la_course'] == 3].shape[0]
    nombre_quatrieme = df_courses[df_courses['place_dans_la_course'] == 4].shape[0]
    nombre_cinquieme = df_courses[df_courses['place_dans_la_course'] == 5].shape[0]
    nombre_disqualifications = df_courses['place_dans_la_course'].isnull().sum()
    place_moyenne = df_courses['place_dans_la_course'].mean()
    if pd.isna(place_moyenne):
        place_moyenne = 0.0
    else:
        place_moyenne = round(place_moyenne, 2)

    # Calculer le montant total gagné
    montant_total_gagne = (
        df_courses[df_courses['place_dans_la_course'] == 1]['montant_offert_1er'].sum() +
        df_courses[df_courses['place_dans_la_course'] == 2]['montant_offert_2eme'].sum() +
        df_courses[df_courses['place_dans_la_course'] == 3]['montant_offert_3eme'].sum() +
        df_courses[df_courses['place_dans_la_course'] == 4]['montant_offert_4eme'].sum() +
        df_courses[df_courses['place_dans_la_course'] == 5]['montant_offert_5eme'].sum()
    )

    return schemas.ChevalResponse(
        nomCheval=db_cheval.nom,
        nombreCoursesEnregistrer=nombre_courses_enregistrer,
        nombreCoursesTotal=db_cheval.nombre_courses,
        precisionPercent=precision,
        vitesseMoyenneKmh=moyenne_vitesse,
        nombrePremier=nombre_premier,
        nombreDeuxieme=nombre_deuxieme,
        nombreTroisieme=nombre_troisieme,
        nombreQuatrieme=nombre_quatrieme,
        nombreCinquieme=nombre_cinquieme,
        nombreDisqualifications=nombre_disqualifications,
        placeMoyenne=place_moyenne,
        montantTotalGagne=montant_total_gagne
    )
# ----------------------------------------------------------------------------------------------------------------------------------------------------------|




# ------------------------------------------------------ Endpoint pour récupérer la généalogie d'un cheval -------------------------------------------------|
def get_complete_info_enfant(nom: str, db: Session, depth: int):

    cheval = db.query(models.ChevauxTrotteurFrancais).filter(models.ChevauxTrotteurFrancais.nom_tf == nom.upper()).first()

    if not cheval:
        raise HTTPException(status_code=404, detail="Cheval non trouvé dans ChevauxTrotteurFrancais")

    infos_pere = get_complete_info_parents(cheval.pere_tf, cheval.annee_naissance_tf, db, depth)
    infos_mere = get_complete_info_parents(cheval.mere_tf, cheval.annee_naissance_tf, db, depth)

    return schemas.GenealogieResponse(
        id=cheval.id_tf,
        nom=cheval.nom_tf,
        sexe=cheval.sexe_tf,
        couleur=cheval.couleur_tf,
        dateDeNaissance=cheval.annee_naissance_tf,
        naisseur=cheval.naisseur_tf,
        lienIfce=cheval.lien_ifce_tf,
        pere=cheval.pere_tf if cheval.pere_tf else "",
        informationsPere=infos_pere,
        mere=cheval.mere_tf if cheval.mere_tf else "",
        informationsMere=infos_mere
    )

def get_complete_info_parents(nom: str, child_birthdate: int, db: Session, depth: int):
    if depth <= 0 or not nom:
        return None

    cheval = db.query(models.ChevauxTrotteurFrancais).filter(
        models.ChevauxTrotteurFrancais.nom_tf == nom.upper(),
        models.ChevauxTrotteurFrancais.annee_naissance_tf <= child_birthdate - 5,
        models.ChevauxTrotteurFrancais.annee_naissance_tf >= child_birthdate - 25
    ).first()

    if not cheval:
        return None

    infos_pere = get_complete_info_parents(cheval.pere_tf, cheval.annee_naissance_tf, db, depth - 1)
    infos_mere = get_complete_info_parents(cheval.mere_tf, cheval.annee_naissance_tf, db, depth - 1)

    return schemas.GenealogieResponse(
        id=cheval.id_tf,
        nom=cheval.nom_tf,
        sexe=cheval.sexe_tf,
        couleur=cheval.couleur_tf,
        dateDeNaissance=cheval.annee_naissance_tf,
        naisseur=cheval.naisseur_tf,
        lienIfce=cheval.lien_ifce_tf,
        pere=cheval.pere_tf if cheval.pere_tf else "",
        informationsPere=infos_pere,
        mere=cheval.mere_tf if cheval.mere_tf else "",
        informationsMere=infos_mere
    )

@app.get(
    "/genealogie-cheval/{nomCheval}/{idCheval}/{depth}",
    response_model=schemas.GenealogieResponse,
    summary="Obtenir la généalogie d'un cheval de la race trotteur français",
    description="Récupère la généalogie complète d'un cheval spécifique, y compris les informations sur les parents et ancêtres jusqu'à une certaine profondeur.",
    tags=["Consultation des informations chevaux"]
)
def get_genealogie_cheval(nomCheval: str, idCheval: int, depth: int = 1, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):

    # Normalisation des noms
    nom_cheval_normalise = nomCheval.upper()

    cheval = db.query(models.ChevauxTrotteurFrancais).filter(
        models.ChevauxTrotteurFrancais.nom_tf == nom_cheval_normalise,
        models.ChevauxTrotteurFrancais.id_tf == idCheval
    ).first()

    if not cheval:
        raise HTTPException(status_code=404, detail="Cheval non trouvé dans ChevauxTrotteurFrancais")

    infos = get_complete_info_enfant(cheval.nom_tf, db, depth)

    return infos
# ----------------------------------------------------------------------------------------------------------------------------------------------------------|



# ------------------------------------------------------ Conditions d'utilisation --------------------------------------------------------------------------|
@app.get(
    "/conditions-utilisation",
    response_class=HTMLResponse,
    summary="URL des conditions d'utilisation",
    description="Permet de voir les conditions d'utilisation de l'API",
    tags=["Conditions d'utilisation et politique de confidentialité"]
)
async def terms_of_service(request: Request):
    return templates.TemplateResponse("conditions_utilisation.html", {"request": request})

@app.get(
    "/politique-de-confidentialite",
    response_class=HTMLResponse,
    summary="URL de la politique de confidentialité",
    description="Permet de voir la politique de confidentialité de l'API",
    tags=["Conditions d'utilisation et politique de confidentialité"]
)
async def privacy_policy(request: Request):
    return templates.TemplateResponse("politique_de_confidentialite.html", {"request": request})
# ----------------------------------------------------------------------------------------------------------------------------------------------------------|


# Lancer le serveur avec Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
