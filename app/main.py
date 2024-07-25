from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from . import models, schemas, database
import pandas as pd

app = FastAPI()

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
@app.get("/stats-ifce/{nomCheval}", response_model=schemas.StatsIfceResponse)
def get_stats_ifce(nomCheval: str, db: Session = Depends(get_db)):


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


# ------------------------------------------------------ Endpoint pour récupérer les stats d'un cheval -----------------------------------------------------|
@app.get("/stat-cheval/{nomCheval}", response_model=schemas.ChevalResponse)
def get_stat_cheval_by_name(nomCheval: str, db: Session = Depends(get_db)):



    # Récupération du nom et vérification de l'existence du cheval dans les courses -----------------------------
    nom_cheval_normalise = nomCheval.upper()
    db_cheval = db.query(models.ParticipationsAuxCourses).filter(models.ParticipationsAuxCourses.nom == nom_cheval_normalise).order_by(desc(models.ParticipationsAuxCourses.id_participation)).first()
    if db_cheval is None:
        raise HTTPException(status_code=404, detail="Le cheval n'a pas de courses enregistrées")
    


    # Récupération du nombre de course et calcul d'une précision ------------------------------------------------
    nombre_courses_enregistrer = db.query(models.ParticipationsAuxCourses).filter(models.ParticipationsAuxCourses.nom == nom_cheval_normalise).count()
    nombre_courses_total = db_cheval.nombre_courses
    precision = (nombre_courses_enregistrer / nombre_courses_total) * 100 if nombre_courses_total > 0 else 0



    # Récupération des courses du cheval ------------------------------------------------------------------------
    query = (db.query(models.Courses, models.ParticipationsAuxCourses)
             .join(models.ParticipationsAuxCourses, models.Courses.id_course == models.ParticipationsAuxCourses.id_course)
             .filter(models.ParticipationsAuxCourses.nom == nom_cheval_normalise))         
    results = query.all()



    # Convertir les résultats de la jointure en DataFrame -------------------------------------------------------
    data = []
    for course, participation in results:
        row = {**course.__dict__, **participation.__dict__}
        row.pop('_sa_instance_state', None)  # Retirer l'état de SQLAlchemy
        data.append(row) 
    df_courses = pd.DataFrame(data)
    print(df_courses)



    # Calcul de la vitesse moyenne ------------------------------------------------------------------------------
    df_courses['temps_en_secondes'] = df_courses['temps_obtenu_en_minute'].apply(convertir_temps_en_secondes)
    df_courses['vitesse'] = df_courses['distance'] / df_courses['temps_en_secondes'] # Calculer la vitesse (distance en mètres / temps en secondes) en m/s
    df_courses['vitesse_km_h'] = df_courses['vitesse'] * 3.6 # Convertir la vitesse en km/h (1 m/s = 3.6 km/h)
    moyenne_vitesse = df_courses['vitesse_km_h'].mean().round(2) # Calculer la moyenne des vitesses en km/h

    
    
    # Calculer le nombre de fois où le cheval est premier, deuxième, etc ----------------------------------------
    nombre_premier = df_courses[df_courses['place_dans_la_course'] == 1].shape[0]
    nombre_deuxieme = df_courses[df_courses['place_dans_la_course'] == 2].shape[0]
    nombre_troisieme = df_courses[df_courses['place_dans_la_course'] == 3].shape[0]
    nombre_quatrieme = df_courses[df_courses['place_dans_la_course'] == 4].shape[0]
    nombre_cinquieme = df_courses[df_courses['place_dans_la_course'] == 5].shape[0]
    nombre_disqualifications = df_courses['place_dans_la_course'].isnull().sum()
    place_moyenne = df_courses['place_dans_la_course'].mean().round(2)



    # Calculer le montant total gagné
    montant_total_gagne = (
        df_courses[df_courses['place_dans_la_course'] == 1]['montant_offert_1er'].sum() +
        df_courses[df_courses['place_dans_la_course'] == 2]['montant_offert_2eme'].sum() +
        df_courses[df_courses['place_dans_la_course'] == 3]['montant_offert_3eme'].sum() +
        df_courses[df_courses['place_dans_la_course'] == 4]['montant_offert_4eme'].sum() +
        df_courses[df_courses['place_dans_la_course'] == 5]['montant_offert_5eme'].sum()
    )



    return schemas.ChevalResponse(
            nomCheval = db_cheval.nom,
            nombreCoursesEnregistrer = nombre_courses_enregistrer,
            nombreCoursesTotal = db_cheval.nombre_courses,
            precisionPercent = precision,
            vitesseMoyenneKmh = moyenne_vitesse,
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

# ------------------------------------------------------ Endpoint pour récupérer les infos d'un cheval -----------------------------------------------------|
def get_complete_info(nom: str, db: Session):

    cheval = db.query(models.ChevauxTrotteurFrancais).filter(models.ChevauxTrotteurFrancais.nom_tf == nom.upper()).first()

    return schemas.GenealogieResponse(
        nom = cheval.nom_tf,
        sexe = cheval.sexe_tf,
        couleur = cheval.couleur_tf,
        dateDeNaissance = cheval.annee_naissance_tf,
        naisseur = cheval.naisseur_tf,
        lienIfce = cheval.lien_ifce_tf,
        pere = cheval.pere_tf,
        mere=cheval.mere_tf,
    )

def get_partial_info(nom: str, db: Session):

    cheval = db.query(models.ParticipationsAuxCourses).filter(models.ParticipationsAuxCourses.nom == nom).order_by(desc(models.ParticipationsAuxCourses.id_participation)).first()

    return schemas.GenealogieResponse(
        nom=cheval.nom,
        sexe=cheval.sexe,
        couleur=cheval.libelle_long_robe,
        dateDeNaissance=None,
        naisseur=None,
        lienIfce=None,
        pere=cheval.nom_pere,
        mere=cheval.nom_mere,
    )

@app.get("/infos-cheval/{nomCheval}", response_model=schemas.InfosResponse)
def get_infos_cheval(nomCheval: str, db: Session = Depends(get_db)):

    # Normalisation des noms
    nom_cheval_normalise = nomCheval.upper()

    cheval = db.query(models.ChevauxTrotteurFrancais).filter(models.ChevauxTrotteurFrancais.nom_tf == nom_cheval_normalise.upper()).first()

    if cheval:
        infos = get_complete_info (cheval.nom_tf, db)

    if not cheval:
        db_cheval_stat = db.query(models.ParticipationsAuxCourses).filter(models.ParticipationsAuxCourses.nom == nom_cheval_normalise).order_by(desc(models.ParticipationsAuxCourses.id_participation)).first()

        if not db_cheval_stat:
            raise HTTPException(status_code=404, detail="Cheval inexistant dans l'ensemble des tables")
        
        elif db_cheval_stat.race != "TROTTEUR FRANCAIS":
            raise HTTPException(status_code=404, detail=f"Le cheval n'est pas un trotteur français, c'est un {db_cheval_stat.race}")
        
        else:
           infos = get_partial_info (db_cheval_stat.nom, db)

    return infos
# ----------------------------------------------------------------------------------------------------------------------------------------------------------|

# ------------------------------------------------------ Endpoint pour récupérer la généalogie d'un cheval -------------------------------------------------|
def get_complete_info_gen(nom: str, db: Session, depth: int):
    cheval = db.query(models.ChevauxTrotteurFrancais).filter(models.ChevauxTrotteurFrancais.nom_tf == nom.upper()).first()
    
    if not cheval:
        raise HTTPException(status_code=404, detail="Cheval non trouvé dans ChevauxTrotteurFrancais")

    infos_pere = get_parent_info_gen(cheval.pere_tf, db, depth)
    infos_mere = get_parent_info_gen(cheval.mere_tf, db, depth)

    return schemas.GenealogieResponse(
        nom=cheval.nom_tf,
        sexe=cheval.sexe_tf,
        couleur=cheval.couleur_tf,
        dateDeNaissance=cheval.annee_naissance_tf,
        naisseur=cheval.naisseur_tf,
        lienIfce=cheval.lien_ifce_tf,
        pere=cheval.pere_tf,
        informationsPere=infos_pere,
        mere=cheval.mere_tf,
        informationsMere=infos_mere
    )

def get_partial_info_gen(nom: str, db: Session, depth: int):
    cheval = db.query(models.ParticipationsAuxCourses).filter(models.ParticipationsAuxCourses.nom == nom).order_by(desc(models.ParticipationsAuxCourses.id_participation)).first()
    
    if not cheval:
        raise HTTPException(status_code=404, detail="Cheval non trouvé dans ParticipationsAuxCourses")

    infos_pere = get_parent_info_gen(cheval.nom_pere, db, depth)
    infos_mere = get_parent_info_gen(cheval.nom_mere, db, depth)

    return schemas.GenealogieResponse(
        nom=cheval.nom,
        sexe=cheval.sexe,
        couleur=cheval.libelle_long_robe,
        dateDeNaissance=None,
        naisseur=None,
        lienIfce=None,
        pere=cheval.nom_pere,
        informationsPere=infos_pere,
        mere=cheval.nom_mere,
        informationsMere=infos_mere
    )


def get_parent_info_gen(nom: str, db: Session, depth: int):
    if depth <= 0 or not nom:
        return None
    try:
        return get_complete_info_gen(nom, db, depth - 1)
    except HTTPException:
        try:
            return get_partial_info_gen(nom, db, depth - 1)
        except HTTPException:
            return None


@app.get("/genealogie-cheval/{nomCheval}", response_model=schemas.GenealogieResponse)
def get_genealogie_cheval(nomCheval: str, db: Session = Depends(get_db), depth: int = 1):

    # Normalisation des noms
    nom_cheval_normalise = nomCheval.upper()

    cheval = db.query(models.ChevauxTrotteurFrancais).filter(models.ChevauxTrotteurFrancais.nom_tf == nom_cheval_normalise.upper()).first()

    if cheval:
        infos = get_complete_info_gen(cheval.nom_tf, db, depth)
    else:
        db_cheval_stat = db.query(models.ParticipationsAuxCourses).filter(models.ParticipationsAuxCourses.nom == nom_cheval_normalise).order_by(desc(models.ParticipationsAuxCourses.id_participation)).first()

        if not db_cheval_stat:
            raise HTTPException(status_code=404, detail="Cheval inexistant dans l'ensemble des tables")
        
        elif db_cheval_stat.race != "TROTTEUR FRANCAIS":
            raise HTTPException(status_code=404, detail=f"Le cheval n'est pas un trotteur français, c'est un {db_cheval_stat.race}")
        
        else:
           infos = get_partial_info_gen(db_cheval_stat.nom, db, depth)

    return infos
# ----------------------------------------------------------------------------------------------------------------------------------------------------------|

# chevaux à test OBJECTION JENILOU


# Lancer le serveur avec Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
