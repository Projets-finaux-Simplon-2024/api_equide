from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class ChevauxTrotteurFrancais(Base):
    __tablename__ = "chevaux_trotteur_francais"
    
    id_tf = Column(Integer, primary_key=True, index=True)
    nom_tf = Column(String, unique=True, nullable=False)
    sexe_tf = Column(String, nullable=False)
    couleur_tf = Column(String)
    annee_naissance_tf = Column(Integer, nullable=False)
    pere_tf = Column(String)
    mere_tf = Column(String)
    date_decee_tf = Column(Date)
    naisseur_tf = Column(String)
    lien_ifce_tf = Column(String)

class ProgrammesDesCourses(Base):
    __tablename__ = "programmes_des_courses"
    
    id_programme = Column(Integer, primary_key=True, index=True)
    date_programme = Column(Date)

class Reunion(Base):
    __tablename__ = "reunion"
    
    id_reunion = Column(String, primary_key=True, index=True)
    id_programme = Column(Integer, ForeignKey("programmes_des_courses.id_programme"), nullable=False)
    num_officiel = Column(Integer)
    nature = Column(String)
    code_hippodrome = Column(String)
    libelle_court_hippodrome = Column(String)
    libelle_long_hippodrome = Column(String)
    code_pays = Column(String)
    libelle_pays = Column(String)
    audience = Column(String)
    statut = Column(String)
    disciplines_mere = Column(String)
    specialite_1 = Column(String)
    specialite_2 = Column(String)
    specialite_3 = Column(String)
    specialite_4 = Column(String)
    meteo_nebulosite_code = Column(String)
    meteo_nebulosite_Libelle_Court = Column(String)
    meteo_nebulosite_Libelle_Long = Column(String)
    meteo_temperature = Column(String)
    meteo_force_vent = Column(String)
    meteo_direction_vent = Column(String)
    
    programme = relationship("ProgrammesDesCourses")

class Courses(Base):
    __tablename__ = "courses"
    
    id_course = Column(Integer, primary_key=True, index=True)
    id_reunion = Column(String, ForeignKey("reunion.id_reunion"), nullable=False)
    libelle = Column(String)
    libelle_court = Column(String)
    heure_depart = Column(Time)
    parcours = Column(String)
    distance = Column(Integer)
    distance_unit = Column(String)
    corde = Column(String)
    discipline = Column(String)
    specialite_1 = Column(String)
    specialite_2 = Column(String)
    condition_sexe = Column(String)
    conditions = Column(String)
    statut = Column(String)
    categorie_statut = Column(String)
    duree_course = Column(Integer)
    duree_course_en_minute = Column(String)
    montant_prix = Column(Integer)
    grand_prix_national_trot = Column(Boolean)
    nombre_declares_partants = Column(Integer)
    montant_total_offert = Column(Integer)
    premier = Column(Integer)
    montant_offert_1er = Column(Integer)
    deuxieme = Column(Integer)
    montant_offert_2eme = Column(Integer)
    troisieme = Column(Integer)
    montant_offert_3eme = Column(Integer)
    quatrieme = Column(Integer)
    montant_offert_4eme = Column(Integer)
    cinquieme = Column(Integer)
    montant_offert_5eme = Column(Integer)
    incidents_type = Column(String)
    incidents_participants = Column(String)
    
    reunion = relationship("Reunion")

class ParticipationsAuxCourses(Base):
    __tablename__ = "participations_aux_courses"
    
    id_participation = Column(Integer, primary_key=True, index=True)
    id_course = Column(Integer, ForeignKey("courses.id_course"), nullable=False)
    nom = Column(String)
    numero_cheval = Column(Integer)
    age = Column(Integer)
    sexe = Column(String)
    race = Column(String)
    statut_au_depart = Column(String)
    proprietaire = Column(String)
    entraineur = Column(String)
    driver = Column(String)
    driverChange = Column(Boolean)
    code_robe = Column(String)
    libelle_court_robe = Column(String)
    libelle_long_robe = Column(String)
    nombre_courses = Column(Integer)
    nombre_victoires = Column(Integer)
    nombre_places = Column(Integer)
    nom_pere = Column(String)
    nom_mere = Column(String)
    place_dans_la_course = Column(Integer)
    jument_pleine = Column(Boolean)
    engagement = Column(Boolean)
    supplement = Column(Integer)
    handicap_distance = Column(Integer)
    poids_condition_monte_change = Column(Boolean)
    temps_obtenu = Column(Integer)
    temps_obtenu_en_minute = Column(String)
    reduction_kilometrique = Column(Integer)
    allure = Column(String)
    
    course = relationship("Courses")
