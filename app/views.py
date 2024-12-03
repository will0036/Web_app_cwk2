from flask import render_template, flash,request,redirect
from app import app,db,models,admin
from flask_admin.contrib.sqla import ModelView
from .forms import LoginForm,RegisterForm,PetForm,ProviderForm,BookingForm,ReviewForm
from datetime import datetime
from flask_login import current_user, login_user, logout_user, login_required
import json

#Allows admin page to view records on the database
admin.add_view(ModelView(models.User, db.session))
admin.add_view(ModelView(models.Pet, db.session))
admin.add_view(ModelView(models.ProviderProfile, db.session))
admin.add_view(ModelView(models.Booking, db.session))
admin.add_view(ModelView(models.Review, db.session))
#Home page
@app.route('/')
def Home():
    topproviders = models.ProviderProfile.query.order_by(models.ProviderProfile.rating.desc()).limit(3).all()
    return render_template('Home.html',
                           title='PetCarePro',
                           header='Home',
                           subheader1='How PetCarePro works',
                           subheader2='Top Rated Providers',
                           topproviders=topproviders)
#Login
@app.route('/login',methods=['GET','POST'])
def Login():
    if current_user.is_authenticated:
        return redirect('/')
    #User is presented with login form and if username and password on database logs user in 
    loginform = LoginForm()
    if loginform.validate_on_submit():
        user= models.User.query.filter_by(username=loginform.username.data).first()
        if user is None or user.password!=loginform.password.data:
            flash('Invalid username or password')
            return redirect('/login')
        login_user(user, remember=True)
        return redirect('/')
    return render_template('Login.html',
                           title='Login',
                           loginform=loginform)
#Logout
@app.route('/logout')
@login_required
def Logout():
    #:ogs out current user
    logout_user()
    return redirect('/')
#Register
@app.route('/register',methods=['GET','POST'])
def Register():
    #Adds a new Owner/Provider to database
    registerform = RegisterForm()
    if registerform.validate_on_submit():
        r = models.User(username= registerform.username.data, password = registerform.password.data, email = registerform.email.data, fname = registerform.fname.data, lname = registerform.lname.data, user_type = registerform.user_type.data)
        db.session.add(r)
        db.session.commit()
        user=models.User.query.filter_by(username=registerform.username.data).first()
        login_user(user,remember=True)
        if(registerform.user_type.data == "Owner"):
            return redirect('/ownerdashboard')
        #If new user a Provider redirects to add provider details form 
        else:
            return redirect('/providerdetails')
    return render_template('Register.html',
                           title='Register',
                           registerform=registerform)
#OwnerDashboard
@app.route('/ownerdashboard',methods=['GET','POST'])
@login_required
def OwnerDashboard():
    user_pets = models.Pet.query.filter_by(owner_id = current_user.get_id() ).all()
    return render_template('OwnerDashboard.html',
                           title = 'UserDashboard',
                           header = 'User Dashboard',
                           subheader1 = 'Manage Pets',
                           user_pets= user_pets)
#ProviderDashboard
@app.route('/providerdashboard',methods=['GET','POST'])
@login_required
def ProviderDashboard():
    provider = models.ProviderProfile.query.filter_by(user_id= current_user.get_id()).first()
    pending = models.Booking.query.filter_by(provider_id = provider.id,status="Pending").all()
    confirmed = models.Booking.query.filter_by(provider_id = provider.id,status="Confirmed").all()
    complete = models.Booking.query.filter_by(provider_id = provider.id,status="Completed").all()
    #Adds confirmed bookings to a dictionary and converts to json for calendar
    if confirmed:
        booked_dates = [
        {'start': c.date_start.strftime('%Y-%m-%dT%H:%M:%S'), 
         'end': c.date_finish.strftime('%Y-%m-%dT%H:%M:%S')}
        for c in confirmed
        ]
    else:
        booked_dates = [] 
    booked_dates_json = json.dumps(booked_dates)
    return render_template('ProviderDashboard.html',
                           title='ProviderDashboard',
                           header = 'Provider Dashboard',
                           subheader1 = 'Pending Bookings',
                           subheader2 = 'Confirmed Bookings',
                           subheader3 = 'Complete Bookings',
                           subheader4 = 'Booking Calendar',
                           pending=pending,
                           confirmed=confirmed,
                           complete=complete,
                           booked_dates= booked_dates_json)
#Confirm Bookings button
@app.route('/confirmbooking/<id>',methods=['GET','POST'])
@login_required
def ConfirmBooking(id):
    data= models.Booking.query.filter_by(id=id).first()
    data.status = "Confirmed"
    db.session.add(data)
    db.session.commit()
    return redirect('/providerdashboard')
#Complete Bookings button
@app.route('/completebooking/<id>',methods=['GET','POST'])
@login_required
def CompleteBooking(id):
    data= models.Booking.query.filter_by(id=id).first()
    data.status = "Complete"
    db.session.add(data)
    db.session.commit()
    return redirect('/providerdashboard')
#Add Pet 
@app.route('/petcreate',methods=['GET','POST'])
@login_required
def AddPet():
    petform = PetForm()
    if petform.validate_on_submit():
        p = models.Pet(name = petform.name.data, species = petform.species.data, breed = petform.breed.data, owner_id = current_user.get_id() )
        db.session.add(p)
        db.session.commit()
        return redirect('/ownerdashboard')
    return render_template('AddPet.html',
                           title = 'Add Pet',
                           petform = petform)
#Edit Pet 
@app.route('/petedit/<id>',methods=['GET','POST'])
@login_required
def EditPet(id):
    petform = PetForm()
    data= models.Pet.query.filter_by(id=id).first()
    petform.name.default = data.name
    petform.species.default = data.species
    petform.breed.default = data.breed
    petform.process()
    if request.method=="POST":
        data.name = request.form['name']
        data.species = request.form['species']
        data.breed = request.form['breed']
        db.session.add(data)
        db.session.commit()
        return redirect('/ownerdashboard')
    return render_template('AddPet.html',
                           title = 'Edit Pet',
                           petform=petform)
#Delete Pet 
@app.route('/petdelete/<id>',methods=['GET','POST'])
@login_required
def DeletePet(id):
    data= models.Pet.query.filter_by(id=id).first()
    db.session.delete(data)
    db.session.commit()
    return redirect('/ownerdashboard')
#Manage Bookings
@app.route('/managebookings/<pet_id>',methods=['GET','POST'])
@login_required
def ManageBookings(pet_id):
    pending = models.Booking.query.filter_by(pet_id = pet_id,status="Pending")
    confirmed = models.Booking.query.filter_by(pet_id = pet_id,status="Confirmed")
    complete = models.Booking.query.filter_by(pet_id = pet_id,status="Completed")
    return render_template('ManageBookings.html',
                           title='Manage Bookings',
                           header='Bookings',
                           subheader1 = "Pending Bookings",
                           subheader2 = "Confirmed Bookings",
                           subheader3 = "Complete Bookings",
                           pending=pending,
                           confirmed=confirmed,
                           complete=complete)
#Provider Details
@app.route('/providerdetails',methods=['GET','POST'])
@login_required
def ProviderDetails():
    providerform = ProviderForm()
    if providerform.validate_on_submit():
        #Changes services from a list to a string seperated by commas for more than one service offered
        services = ""
        if (len(providerform.services_offered.data)>1):
            for x in range(len(providerform.services_offered.data)):
                services = services + providerform.services_offered.data[x] + ", "
            #Removes last comma and space
            services = services[:-2]
        else:
            services = providerform.services_offered.data[0]
        p = models.ProviderProfile(user_id= current_user.get_id(), services_offered = services, country = providerform.country.data, city = providerform.city.data, postcode = providerform.postcode.data)
        db.session.add(p)
        db.session.commit()
        return redirect('/')
    return render_template('ProviderDetails.html',
                           title = 'Provider Detials',
                           providerform=providerform)
#Edit ProviderDetails
@app.route('/providerdetailsedit',methods=['GET','POST'])
@login_required
def EditProvider():
    providerform = ProviderForm()
    data= models.ProviderProfile.query.filter_by(user_id=current_user.get_id()).first()
    #loads old data into form
    providerform.country.default = data.country
    providerform.city.default = data.city
    providerform.postcode.default = data.postcode
    providerform.process()
    if request.method=="POST":
        data.country = request.form['country']
        data.city = request.form['city']
        data.postcode = request.form['postcode']
        db.session.add(data)
        db.session.commit()
        return redirect('/providerdashboard')
    return render_template('ProviderDetails.html',
                           title = 'Edit Provider Details',
                           providerform=providerform)
#Search page
@app.route('/search',methods=['GET','POST'])
@login_required
def Search():
    providers = models.ProviderProfile.query.all()
    return render_template('Search.html',
                           title = 'search',
                           providers=providers)
#View Provider Profile
@app.route('/viewproviderprofile/<id>',methods=['GET','POST'])
@login_required
def viewProviderProfile(id):
    provider = models.ProviderProfile.query.filter_by(id=id).first()
    bookings = models.Booking.query.filter_by(provider_id=id,status="Confirmed").all()
    topreviews = models.Review.query.filter_by(provider_id=id).order_by(models.Review.rating.desc()).limit(3).all()
    #Adds confirmed bookings to a dictionary and converts to json for calendar
    if bookings:
        booked_dates = [
        {'start': b.date_start.strftime('%Y-%m-%dT%H:%M:%S'), 
         'end': b.date_finish.strftime('%Y-%m-%dT%H:%M:%S')}
        for b in bookings
        ]
    else:
        booked_dates = [] 
    booked_dates_json = json.dumps(booked_dates)
    return render_template('ProviderProfile.html',
                           title='Provider Profile',
                           provider= provider,
                           subheader1 = "Booked Dates",
                           subheader2 = "Reviews",
                           booked_dates =booked_dates_json,
                           topreviews=topreviews)
#CreateBooking
@app.route('/createbooking/<provider_id>',methods=['GET','POST'])
@login_required
def CreateBooking(provider_id):
    bookingform = BookingForm()
    pet_name = []
    pets = models.Pet.query.filter_by(owner_id= current_user.get_id()).all()
    provider = models.ProviderProfile.query.filter_by(id=provider_id).first()
    services = provider.services_offered.split(", ")
    #Adds all of a users pets to a list so user can choose
    for p in pets:
        pet_name.append(p.name)
    bookingform.pet.choices = pet_name
    bookingform.service.choices = services
    bookingform.provider_id.data = provider_id
    if bookingform.validate_on_submit():
        pet_id = models.Pet.query.filter_by(name=bookingform.pet.data, owner_id=current_user.get_id()).first().id
        b = models.Booking(pet_id=pet_id, provider_id=provider_id, service=bookingform.service.data, date_start = bookingform.date_start.data, date_finish = bookingform.date_finish.data, status="Pending")
        db.session.add(b)
        db.session.commit()
        return redirect('/ownerdashboard')
    return render_template('CreateBooking.html',
                           title = 'Create Booking',
                           bookingform=bookingform)
#CreateReview
@app.route('/createreview/<owner_id>/<provider_id>',methods=['GET','POST'])
@login_required
def CreateReview(owner_id,provider_id):
    reviewform = ReviewForm()
    if reviewform.validate_on_submit():
        r = models.Review(owner_id=owner_id, provider_id=provider_id,rating = reviewform.rating.data, comment = reviewform.comment.data)
        db.session.add(r)
        db.session.commit()
        return redirect("{{url_for('calculaterating',provider_id=provider_id)}}")
    return render_template('CreateReview.html',
                           title= 'Create Review',
                           reviewform = reviewform)
#CalculateRating 
@app.route('/calculaterating/<provider_id>',methods=['GET','POST'])
@login_required
def CalculateRating(provider_id):
    #Returns all reviews for the provider
    ratings = models.Review.query.filter_by(provider_id=provider_id).all()
    provider = models.ProviderProfile.query.filter_by(id=provider_id).first()
    #Calculates average of all the ratings for review
    x= 0
    for i in (ratings):
        x += i.rating
    x= x/len(ratings)
    provider.rating = x
    db.session.add(provider)
    db.session.commit()
    return redirect('/ownerdashboard')
#Reviews
@app.route('/reviews/<provider_id>',methods=['GET','POST'])
@login_required
def Reviews(provider_id):
    reviews = models.Review.query.filter_by(provider_id=provider_id).order_by(models.Review.rating.desc()).all()
    return render_template('Reviews.html',
                           title = "Reviews",
                           header = "Reviews",
                           reviews= reviews)