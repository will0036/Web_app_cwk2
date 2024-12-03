from app import app,db
from app.models import User, Pet, ProviderProfile, Booking, Review
from faker import Faker
import random
from datetime import datetime, timedelta
import sys

#initialise faker
faker = Faker()
#Create n fake users
def create_fake_user(n):
    for x in range(n):
        user = User(username=faker.user_name(),password=faker.password(),email=faker.email(),fname=faker.first_name(),lname=faker.last_name(),user_type=random.choice(['Owner', 'Provider']),)
        db.session.add(user)
    db.session.commit()
#Create n fake pets for each owner 
def create_fake_pets(n):
    owners= User.query.filter_by(user_type='Owner').all()
    for o in owners:
        for x in range(n):
            pet = Pet(name=faker.first_name(),species=faker.word(),breed=faker.word(),owner_id= o.id)
            db.session.add(pet)
    db.session.commit()
#Create provider profile for each provider in users
def create_fake_provider_profile():
    providers= User.query.filter_by(user_type='Provider').all()
    for p in providers:
        profile = ProviderProfile.query.filter_by(user_id= p.id).first()
        if not profile:
            service_offered_list=["Grooming","Daycare","Walking","Training","Veterinary Services","Overnightcare"]
            random_service_offered_list= random.sample(service_offered_list,random.randint(1,5))
            services = ""
            for i in range(len(random_service_offered_list)):
                services = services + random_service_offered_list[i] + ", "
            services = services[:-2]
            providerprofile = ProviderProfile(user_id = p.id, services_offered= services, country=faker.country(), city=faker.city(), postcode=faker.zipcode())
            db.session.add(providerprofile)
    db.session.commit()
#Create n fake bookings for each pet
def create_fake_bookings(n):
    pets = Pet.query.all()
    providers= ProviderProfile.query.all()
    for p in pets:
        for x in range(n):
            provider = random.choice(providers)
            while True:
                start_date = faker.date_time_between_dates(datetime(2024, 10, 1, 12, 0, 0),datetime(2025, 2, 1, 12, 0, 0))
                finish_date = start_date + timedelta(hours=random.randint(1, 48))
                current_date = datetime.now()
                if start_date < current_date :
                    status = "Completed"
                else:
                    status = random.choice(["Pending","Confirmed"])       
                overlapping_bookings = Booking.query.filter(Booking.provider_id == provider.id, Booking.date_finish > start_date, Booking.date_start < finish_date, Booking.status != "Pending").all()
                if not overlapping_bookings:
                    break
            service_list = provider.services_offered.split(", ")
            booking = Booking(pet_id = p.id, provider_id = provider.id, service = random.choice(service_list), date_start = start_date, date_finish = finish_date, status=status)
            db.session.add(booking)
            db.session.commit()
#Create a fake review for each completed booking
def create_fake_review():
    bookings = Booking.query.filter_by(status="Completed").all()
    for b in bookings:
        rating = random.choice([1.0,1.5,2.0,2.5,3.0,3.5,4.0,4.5,5.0])
        review = Review(owner_id= b.pet.owner_id, provider_id= b.provider_id, booking_id=b.id, rating= rating, comment= faker.paragraph(nb_sentences=5))
        db.session.add(review)
        db.session.commit()
        ratings = Review.query.filter_by(provider_id=b.provider_id).all()
        provider = ProviderProfile.query.filter_by(id=b.provider_id).first()
        x= 0
        for i in (ratings):
            x += i.rating
        x= x/len(ratings)
        provider.rating = x
        db.session.add(provider)
    db.session.commit()
#Create n fake users
def populate_database(n):
    create_fake_user(n)
    create_fake_pets(random.randint(1,3))
    create_fake_provider_profile()
    create_fake_bookings(random.randint(1,3))
    create_fake_review()
if __name__=="__main__":
    if len(sys.argv) <= 1:
        print('Pass the number of users you want to create as an argument.')
        sys.exit(1)
    with app.app_context():
        populate_database(int(sys.argv[1]))