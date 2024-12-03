from flask_wtf import FlaskForm
from wtforms import widgets,SelectField, StringField,PasswordField, EmailField, IntegerField, SelectMultipleField,DateTimeLocalField,FloatField,TextAreaField
from wtforms.validators import DataRequired, StopValidation,ValidationError,NumberRange
from .models import Booking, ProviderProfile
from markupsafe import Markup
from datetime import datetime

class BootstrapListWidget(widgets.ListWidget):
    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        html = [f"<{self.html_tag} {widgets.html_params(**kwargs)}>"]
        for subfield in field:
            if self.prefix_label:
                html.append(f"<li class='list-group-item'>{subfield.label} {subfield(class_='form-check-input ms-1')}</li>")
            else:
                html.append(f"<li class='list-group-item'>{subfield(class_='form-check-input me-1')} {subfield.label}</li>")
        html.append("</%s>" % self.html_tag)
        return Markup("".join(html))
    
# Form field class for multiple radio feilds
class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

# Validator class for MultipleCheckBoxField
class MultiCheckboxValidate():
    def __init__(self, message=None):
        if not message:
            message = 'At least one option must be selected.'
        self.message = message
    def __call__(self, form, field):
        if len(field.data) == 0:
            raise StopValidation(self.message)
        
# Validator class for checking if the start date is before current date  
class StartDateValidator():
    def __init__(self, message=None):
        if not message:
            message = 'The start date must be in the future.'
        self.message = message
    def __call__(self, form, field):
        if field.data <= datetime.now():
            raise ValidationError(self.message)
        
# Validator class for checking if the finish date is after the start date
class FinishDateValidator():
    def __init__(self, message=None):
        if not message:
            message = 'The finish date must be after the start date.'
        self.message = message
    def __call__(self, form, field):
        if form.date_start.data and field.data <= form.date_start.data:
            raise ValidationError(self.message)
        
# Validator class for checking if the booking time overlaps with existing bookings
class BookingOverlapValidator():
    def __init__(self, message=None):
        if not message:
            message = 'The selected time overlaps with an existing booking.'
        self.message = message
    def __call__(self, form, field):
        provider_id = form.provider_id.data 
        date_start = form.date_start.data
        date_finish = form.date_finish.data
        overlapping_bookings = Booking.query.filter(Booking.provider_id == provider_id, Booking.date_finish > date_start, Booking.date_start < date_finish, Booking.status != "Pending").all()
        if overlapping_bookings:
            raise ValidationError(self.message)
        
#Creates a flask-wtf form class for logging in
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

#Creates a flask-wtf form class for registering
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    fname = StringField('First Name', validators=[DataRequired()])
    lname = StringField('Last Name', validators=[DataRequired()])
    user_type = SelectField('User type',choices=["Owner","Provider"],validators=[DataRequired()] )

#Creates a flask-wtf form class for adding a pet
class PetForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    species = StringField('Species', validators=[DataRequired()])
    breed = StringField('Breed', validators=[DataRequired()])

#Creates a flask-wtf form class for adding provider detials
class ProviderForm(FlaskForm):
    services_offered = MultiCheckboxField('Services Offered',choices=["Grooming","Daycare","Walking","Training","Veterinary Services","Overnightcare"], validators=[MultiCheckboxValidate()])
    country = StringField('Country', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    postcode = StringField('Postcode', validators=[DataRequired()])

#Creates a flask-wtf form class for creating a booking
class BookingForm(FlaskForm):
    pet = SelectField('Pet',validators=[DataRequired()])
    service = SelectField('Service',validators=[DataRequired()])
    date_start = DateTimeLocalField('Start Date', format='%Y-%m-%dT%H:%M', validators=[DataRequired(), StartDateValidator()])
    date_finish = DateTimeLocalField('End Date', format='%Y-%m-%dT%H:%M', validators=[DataRequired(), FinishDateValidator(),BookingOverlapValidator()])
    provider_id = IntegerField('Provider', validators=[DataRequired()])

#Creates a flask-wtf form class for creating a review
class ReviewForm(FlaskForm):
    comment = TextAreaField('Comment',validators=[DataRequired()])
    rating = FloatField('Rating',validators=[DataRequired(),NumberRange(min=1, max=5)])
    

