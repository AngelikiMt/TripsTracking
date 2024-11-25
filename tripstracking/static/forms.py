from wtforms import StringField, PasswordField, Form, EmailField
from wtforms.validators import DataRequired, Email, Length

class RegisterForm(Form):
    fullname = StringField("Fullname", validators = [DataRequired(), Length(min=3, max=20)])
    password = PasswordField("Password", validators = [DataRequired(), Length(min=10, max=20)])
    username = StringField("Username", validators = [DataRequired(), Length(min=3, max=20)])
    email = EmailField("Email", validators = [DataRequired(), Email()])
