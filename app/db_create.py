from config import SQLALCHEMY_DATABASE_URI
from app import db
import os.path

#creates databases 
db.create_all()