from app import db,login_manager
from flask_login import UserMixin

# Get user id as an int
@login_manager.user_loader
def load_user(id):
    return db.session.get(User, int(id))

# Association Table for Many-to-Many (Users <-> Bookings)
user_booking_association = db.Table(
    "user_booking",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("booking_id", db.Integer, db.ForeignKey("bookings.id"), primary_key=True)
)

# User Table
class User(UserMixin,db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), index=True)
    password = db.Column(db.String(50), index=True)
    email = db.Column(db.String(50))
    fname = db.Column(db.String(50))
    lname = db.Column(db.String(50))
    user_type = db.Column(db.String(50))
    
    # Relationships
    pets = db.relationship('Pet', backref='owner', lazy='dynamic')
    provider_profile = db.relationship('ProviderProfile', backref='user', uselist=False)
    bookings = db.relationship('Booking', secondary=user_booking_association, backref='users', lazy='dynamic')
    reviews = db.relationship('Review', backref='users', lazy='dynamic')

# Pet Table
class Pet(db.Model):
    __tablename__ = "pets"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), index=True)
    species = db.Column(db.String(50))
    breed = db.Column(db.String(50))
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    #Relationship
    bookings = db.relationship('Booking', backref='pet', lazy='dynamic')

#ProviderProfile Table
class ProviderProfile(db.Model):
    __tablename__ = "provider_profiles"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    services_offered = db.Column(db.String(1000))
    country = db.Column(db.String(100))
    city = db.Column(db.String(100))
    postcode = db.Column(db.String(100))
    rating = db.Column(db.Float)

#Booking Table
class Booking(db.Model):
    __tablename__ = "bookings"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pets.id'))
    provider_id = db.Column(db.Integer, db.ForeignKey('provider_profiles.id'))
    service = db.Column(db.String(1000))
    date_start = db.Column(db.DateTime)
    date_finish = db.Column(db.DateTime)
    status = db.Column(db.String(20))

    #Relationship
    provider = db.relationship('ProviderProfile', backref='bookings')

#Review Table
class Review(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    provider_id = db.Column(db.Integer, db.ForeignKey('provider_profiles.id'))
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'))
    rating = db.Column(db.Float)
    comment = db.Column(db.String(10000))

    # Relationship
    booking = db.relationship('Booking', backref='review')
    

