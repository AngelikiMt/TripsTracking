from wtforms import StringField, PasswordField, Form, SubmitField, EmailField, TextAreaField, DateField, DecimalField
from wtforms.validators import DataRequired, Email, Length

class RegisterForm(Form):
    fullname = StringField("Fullname", validators = [DataRequired(), Length(min=3, max=20)])
    password = PasswordField("Password", validators = [DataRequired(), Length(min=10, max=20)])
    username = StringField("Username", validators = [DataRequired(), Length(min=3, max=20)])
    email = EmailField("Email", validators = [DataRequired(), Email()])
    submit = SubmitField("Submit")

class LoginForm(Form):
    fullname = StringField("Fullname", validators = [DataRequired(), Length(min=3, max=20)])
    password = PasswordField("Password", validators = [DataRequired(), Length(min=10, max=20)])
    submit = SubmitField("Submit")

class PutTripForm(Form):
    destination = StringField("Destination", validators=[DataRequired(), Length(max=20)])
    date = DateField("Date")
    description = TextAreaField("Description", validators=[DataRequired(), Length(max=100)])
    budget = DecimalField("Budget")
    submit = SubmitField("Submit")

class AddTripForm(Form):
    destination = StringField("Destination", validators=[DataRequired(), Length(max=20)])
    date = DateField("Date")
    description = TextAreaField("Description", validators=[DataRequired(), Length(max=100)])
    budget = DecimalField("Budget")
    submit = SubmitField("Submit")
