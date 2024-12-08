from wtforms import StringField, PasswordField, Form, EmailField, TextAreaField, DateField, DecimalField
from wtforms.validators import DataRequired, Email, Length

class RegisterForm(Form):
    fullname = StringField("Fullname", validators = [DataRequired(), Length(min=3, max=20)])
    password = PasswordField("Password", validators = [DataRequired(), Length(min=10, max=20)])
    username = StringField("Username", validators = [DataRequired(), Length(min=3, max=20)])
    email = EmailField("Email", validators = [DataRequired(), Email()])

class LoginForm(Form):
    fullname = StringField("Fullname", validators = [DataRequired(), Length(min=3, max=20)])
    password = PasswordField("Password", validators = [DataRequired(), Length(min=10, max=20)])

class PutTripForm(Form):
    destination = StringField("Destination", validators=[DataRequired(), Length(max=20)])
    date = DateField("Date")
    description = TextAreaField("Description", validators=[DataRequired(), Length(max=100)])
    budget = DecimalField("Budget")

class AddTripForm(Form):
    destination = StringField("Destination", validators=[DataRequired(), Length(max=20)])
    date = DateField("Date")
    description = TextAreaField("Description", validators=[DataRequired(), Length(max=100)])
    budget = DecimalField("Budget")