from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from . import models, schemas, database
import json
from datetime import time

app = FastAPI()

# Dépendance pour obtenir une session de base de données
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/resultat/{nomCheval}", response_model=schemas.ChevalResponse)
def get_cheval_by_name(nomCheval: str, db: Session = Depends(get_db)):

    # Convertir le nom du cheval en majuscules pour la recherche
    nom_cheval_normalise = nomCheval.upper()

    db_cheval = db.query(models.ParticipationsAuxCourses).filter(models.ParticipationsAuxCourses.nom == nom_cheval_normalise).order_by(desc(models.ParticipationsAuxCourses.id_participation)).first()

    if db_cheval is None:
        raise HTTPException(status_code=404, detail="Cheval not found")
    
    nombre_courses_enregistrer = db.query(models.ParticipationsAuxCourses).filter(models.ParticipationsAuxCourses.nom == nom_cheval_normalise).count()

    # Calculer la précision
    nombre_courses_total = db_cheval.nombre_courses
    precision = (nombre_courses_enregistrer / nombre_courses_total) * 100 if nombre_courses_total > 0 else 0

    # Effectuer la jointure pour obtenir les détails des courses
    jointure = db.query(models.Courses).join(models.ParticipationsAuxCourses, models.Courses.id_course == models.ParticipationsAuxCourses.id_course).filter(models.ParticipationsAuxCourses.nom == nom_cheval_normalise).all()
    
    # Convertir les résultats de la jointure en dictionnaires et les imprimer
    jointure_dicts = []
    for course in jointure:
        course_dict = {column.name: (str(getattr(course, column.name)) if isinstance(getattr(course, column.name), time) else getattr(course, column.name)) for column in course.__table__.columns}
        jointure_dicts.append(course_dict)
        print(json.dumps(course_dict, indent=4))

    return schemas.ChevalResponse(
            nomCheval=db_cheval.nom,
            nombreCoursesEnregistrer=nombre_courses_enregistrer,
            nombreCoursesTotal=db_cheval.nombre_courses,
            precisionPercent=precision
        )

# Lancer le serveur avec Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
