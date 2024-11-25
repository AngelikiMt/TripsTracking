from wtforms import StringField, PasswordField, Form
from wtforms.validators import DataRequired, Email

class RegisterForm(Form):
    fullname = StringField("Fullname", validators = [DataRequired()])
    password = PasswordField("Password", validators = [DataRequired()])
    username = StringField("Username", validators = [DataRequired(), Email()])
    email = StringField("Email", validators = [DataRequired()])
