from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from . import models, schemas, database
from typing import Optional, Dict, Any
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



# ------------------------------------------------------ Endpoint pour récupérer la généalogie d'un cheval -------------------------------------------------|
def get_genealogie(nom: str, db: Session, depth: int = 0, max_depth: int = 1) -> Optional[schemas.GenealogieCheval]:
    if depth > max_depth:
        return None

    # Normaliser le nom en majuscules
    nom_normalise = nom.upper()
    
    cheval = db.query(models.ChevauxTrotteurFrancais).filter(models.ChevauxTrotteurFrancais.nom_tf == nom_normalise).first()
    nom_parents_via_participations = db.query(models.ParticipationsAuxCourses).filter(models.ParticipationsAuxCourses.nom == nom_normalise).first()

    if cheval:
        pere = get_genealogie(cheval.pere_tf, db, depth + 1, max_depth) if cheval.pere_tf else None
        mere = get_genealogie(cheval.mere_tf, db, depth + 1, max_depth) if cheval.mere_tf else None
        return schemas.GenealogieCheval(
            nom=cheval.nom_tf,
            sexe=cheval.sexe_tf,
            couleur=cheval.couleur_tf,
            dateDeNaissance=cheval.annee_naissance_tf,
            naisseur=cheval.naisseur_tf,
            lienIfce=cheval.lien_ifce_tf,
            pere=pere if pere else schemas.GenealogieCheval(nom=cheval.pere_tf, sexe=None, couleur=None, dateDeNaissance=None, naisseur=None, lienIfce=None, pere=None, mere=None) if cheval.pere_tf else None,
            mere=mere if mere else schemas.GenealogieCheval(nom=cheval.mere_tf, sexe=None, couleur=None, dateDeNaissance=None, naisseur=None, lienIfce=None, pere=None, mere=None) if cheval.mere_tf else None
        )
    elif nom_parents_via_participations:
        pere = get_genealogie(nom_parents_via_participations.nom_pere, db, depth + 1, max_depth) if nom_parents_via_participations.nom_pere else None
        mere = get_genealogie(nom_parents_via_participations.nom_mere, db, depth + 1, max_depth) if nom_parents_via_participations.nom_mere else None

        # Si nous avons trouvé des noms de parents via ParticipationsAuxCourses, essayons de récupérer leurs infos complètes
        if pere and isinstance(pere, schemas.GenealogieCheval) and pere.nom:
            pere_info = db.query(models.ChevauxTrotteurFrancais).filter(models.ChevauxTrotteurFrancais.nom_tf == pere.nom.upper()).first()
            if pere_info:
                pere = schemas.GenealogieCheval(
                    nom=pere_info.nom_tf,
                    sexe=pere_info.sexe_tf,
                    couleur=pere_info.couleur_tf,
                    dateDeNaissance=pere_info.annee_naissance_tf,
                    naisseur=pere_info.naisseur_tf,
                    lienIfce=pere_info.lien_ifce_tf,
                    pere=None,  # Ces champs seront remplis récursivement
                    mere=None
                )

        if mere and isinstance(mere, schemas.GenealogieCheval) and mere.nom:
            mere_info = db.query(models.ChevauxTrotteurFrancais).filter(models.ChevauxTrotteurFrancais.nom_tf == mere.nom.upper()).first()
            if mere_info:
                mere = schemas.GenealogieCheval(
                    nom=mere_info.nom_tf,
                    sexe=mere_info.sexe_tf,
                    couleur=mere_info.couleur_tf,
                    dateDeNaissance=mere_info.annee_naissance_tf,
                    naisseur=mere_info.naisseur_tf,
                    lienIfce=mere_info.lien_ifce_tf,
                    pere=None,  # Ces champs seront remplis récursivement
                    mere=None
                )

        return schemas.GenealogieCheval(
            nom=nom,
            sexe=None,
            couleur=None,
            dateDeNaissance=None,
            naisseur=None,
            lienIfce=None,
            pere=pere if pere else schemas.GenealogieCheval(nom=nom_parents_via_participations.nom_pere, sexe=None, couleur=None, dateDeNaissance=None, naisseur=None, lienIfce=None, pere=None, mere=None) if nom_parents_via_participations.nom_pere else None,
            mere=mere if mere else schemas.GenealogieCheval(nom=nom_parents_via_participations.nom_mere, sexe=None, couleur=None, dateDeNaissance=None, naisseur=None, lienIfce=None, pere=None, mere=None) if nom_parents_via_participations.nom_mere else None
        )

    return None

@app.get("/genealogie-cheval/{nomCheval}", response_model=schemas.GenealogieResponse)
def get_genealogie_cheval(nomCheval: str, db: Session = Depends(get_db)):
    nom_cheval_normalise = nomCheval.upper()
    genealogie_cheval = get_genealogie(nom_cheval_normalise, db)

    if not genealogie_cheval:
        db_cheval_stat = db.query(models.ParticipationsAuxCourses).filter(models.ParticipationsAuxCourses.nom == nom_cheval_normalise).order_by(desc(models.ParticipationsAuxCourses.id_participation)).first()
        if not db_cheval_stat:
            raise HTTPException(status_code=404, detail="Cheval inexistant dans l'ensemble des tables")
        else:
            raise HTTPException(status_code=404, detail=f"Le cheval n'est pas un trotteur français, c'est un {db_cheval_stat.race}")

    return schemas.GenealogieResponse(
        nomCheval=genealogie_cheval.nom,
        sexeCheval=genealogie_cheval.sexe,
        couleurCheval=genealogie_cheval.couleur,
        dateDeNaissance=genealogie_cheval.dateDeNaissance,
        naisseur=genealogie_cheval.naisseur,
        lienIfce=genealogie_cheval.lienIfce,
        pere=genealogie_cheval.pere,
        mere=genealogie_cheval.mere
    )
# ----------------------------------------------------------------------------------------------------------------------------------------------------------|

# Lancer le serveur avec Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
