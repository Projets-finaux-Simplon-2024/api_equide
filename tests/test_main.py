import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app, get_db, convertir_temps_en_secondes
from app import models, schemas, database
from datetime import date, time

# Configuration de la base de données pour les tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dépendance pour obtenir une session de base de données
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Créer un client de test
client = TestClient(app)

@pytest.fixture(scope="module")
def setup_database():
    # Créer les tables de la base de données
    models.Base.metadata.create_all(bind=engine)
    
    # Ajouter des données de test
    db = TestingSessionLocal()

    # Ajouter des programmes des courses
    programme = models.ProgrammesDesCourses(id_programme=1, date_programme=date(2023, 7, 28))
    db.add(programme)
    db.commit()

    # Ajouter des réunions
    reunion = models.Reunion(id_reunion="R1", id_programme=1, num_officiel=1, nature="NATURE", code_hippodrome="CODE", libelle_court_hippodrome="COURT", libelle_long_hippodrome="LONG", code_pays="FR", libelle_pays="France", audience="A", statut="ST", disciplines_mere="DM", specialite_1="S1", specialite_2="S2", specialite_3="S3", specialite_4="S4", meteo_nebulosite_code="MNC", meteo_nebulosite_Libelle_Court="MLC", meteo_nebulosite_Libelle_Long="MLL", meteo_temperature="25", meteo_force_vent="10", meteo_direction_vent="N")
    db.add(reunion)
    db.commit()

    # Ajouter des courses
    courses = [
        models.Courses(id_course=1, id_reunion="R1", libelle="Course 1", libelle_court="C1", heure_depart=time(12, 0), parcours="P", distance=2000, distance_unit="m", corde="C", discipline="D", specialite_1="S1", specialite_2="S2", condition_sexe="CS", conditions="C", statut="S", categorie_statut="CS", duree_course=120, duree_course_en_minute="2m 0s", montant_prix=1000, grand_prix_national_trot=True, nombre_declares_partants=10, montant_total_offert=2000, premier=1, montant_offert_1er=1000, deuxieme=2, montant_offert_2eme=500, troisieme=3, montant_offert_3eme=300, quatrieme=4, montant_offert_4eme=200, cinquieme=5, montant_offert_5eme=100, incidents_type="IT", incidents_participants="IP"),
        models.Courses(id_course=2, id_reunion="R1", libelle="Course 2", libelle_court="C2", heure_depart=time(14, 0), parcours="P", distance=1500, distance_unit="m", corde="C", discipline="D", specialite_1="S1", specialite_2="S2", condition_sexe="CS", conditions="C", statut="S", categorie_statut="CS", duree_course=90, duree_course_en_minute="1m 30s", montant_prix=800, grand_prix_national_trot=False, nombre_declares_partants=8, montant_total_offert=1600, premier=1, montant_offert_1er=800, deuxieme=2, montant_offert_2eme=400, troisieme=3, montant_offert_3eme=200, quatrieme=4, montant_offert_4eme=100, cinquieme=5, montant_offert_5eme=50, incidents_type="IT", incidents_participants="IP")
    ]
    db.add_all(courses)
    db.commit()

    # Ajouter des chevaux
    chevaux = [
        models.ChevauxTrotteurFrancais(id_tf=1, nom_tf="TEST_CHEVAL_1", sexe_tf="M", couleur_tf="BAI", annee_naissance_tf=2010, naisseur_tf="TEST_NAISS", lien_ifce_tf="http://test.com", pere_tf="TEST_PERE", mere_tf="TEST_MERE"),
        models.ChevauxTrotteurFrancais(id_tf=2, nom_tf="TEST_CHEVAL_2", sexe_tf="F", couleur_tf="ALEZAN", annee_naissance_tf=2012, naisseur_tf="TEST_NAISS", lien_ifce_tf="http://test.com", pere_tf="TEST_PERE", mere_tf="TEST_MERE")
    ]
    db.add_all(chevaux)
    db.commit()

    # Ajouter des participations aux courses
    participations = [
        models.ParticipationsAuxCourses(id_participation=1, id_course=1, nom="TEST_CHEVAL_1", race="TROTTEUR FRANCAIS", nombre_courses=10),
        models.ParticipationsAuxCourses(id_participation=2, id_course=2, nom="TEST_CHEVAL_2", race="TROTTEUR FRANCAIS", nombre_courses=8)
    ]
    db.add_all(participations)
    db.commit()
    
    db.close()
    yield
    # Supprimer les tables de la base de données
    models.Base.metadata.drop_all(bind=engine)

def get_access_token(client):
    response = client.post(
        "/auth/token",
        data={"username": "admin", "password": "admin"},
    )
    return response.json()["access_token"]

def test_get_chevaux(setup_database):
    access_token = get_access_token(client)
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/chevaux/?page=1&page_size=10", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_results"] == 2
    assert data["total_pages"] == 1
    assert data["current_page"] == 1
    assert len(data["results"]) == 2

def test_get_stats_ifce(setup_database):
    access_token = get_access_token(client)
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/stats-ifce/TEST_CHEVAL_1", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["dispoIFCE"] == "Oui"
    assert data["lienIfce"] == "http://test.com"
    assert data["dispoStats"] == "1 courses sont disponibles"
    assert data["race"] == "Le cheval est un TROTTEUR FRANCAIS"

def test_get_infos_cheval(setup_database):
    access_token = get_access_token(client)
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/infos-cheval/1", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["nom"] == "TEST_CHEVAL_1"
    assert data["sexe"] == "M"

def test_get_stat_cheval_by_name(setup_database):
    access_token = get_access_token(client)
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/stat-cheval/TEST_CHEVAL_1", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["nomCheval"] == "TEST_CHEVAL_1"
    assert data["nombreCoursesEnregistrer"] == 1

def test_convertir_temps_en_secondes():
    assert convertir_temps_en_secondes("1m 30s") == 90
    assert convertir_temps_en_secondes("0m 45s") == 45
    assert convertir_temps_en_secondes("0m 0s") == None
