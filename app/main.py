from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from . import models, schemas
from .database import SessionLocal, engine

# Créer les tables de la base de données
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dépendance pour obtenir la session de base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint pour récupérer les données de course d'un cheval
@app.post("/cheval", response_model=schemas.ChevalWithParticipations)
def get_course_data(request: schemas.ChevalRequest, db: Session = Depends(get_db)):
    cheval = db.query(models.ChevauxTrotteurFrancais).filter(models.ChevauxTrotteurFrancais.nom_tf == request.nom_tf).first()
    if not cheval:
        raise HTTPException(status_code=404, detail="Cheval not found")
    participations = db.query(models.ParticipationsAuxCourses).filter(models.ParticipationsAuxCourses.nom == request.nom_tf).all()
    return schemas.ChevalWithParticipations(cheval=cheval, participations=participations)

# Fonction récursive pour récupérer la généalogie
def get_genealogy(db: Session, nom_tf: str, generations: int):
    cheval = db.query(models.ChevauxTrotteurFrancais).filter(models.ChevauxTrotteurFrancais.nom_tf == nom_tf).first()
    if not cheval or generations == 0:
        return None
    
    pere = get_genealogy(db, cheval.pere_tf, generations - 1) if cheval.pere_tf else None
    mere = get_genealogy(db, cheval.mere_tf, generations - 1) if cheval.mere_tf else None
    
    return schemas.Genealogy(
        cheval=cheval,
        pere=pere,
        mere=mere
    )

# Endpoint pour récupérer la généalogie d'un cheval
@app.post("/genealogie", response_model=schemas.Genealogy)
def get_genealogy_endpoint(request: schemas.ChevalRequest, generations: int = 3, db: Session = Depends(get_db)):
    genealogy = get_genealogy(db, request.nom_tf, generations)
    if not genealogy:
        raise HTTPException(status_code=404, detail="Généalogie not found")
    return genealogy
