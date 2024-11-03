from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField
from wtforms.validators import InputRequired, Length, Email, EqualTo

class RegisterForm(FlaskForm):
    """Registration form for new users--username, email, password & confirm password"""

    username=StringField("Username", validators=
                         [InputRequired(message="Required"), 
                          Length(max=20, message="Username must be less than 20 characters")])
    
    email=EmailField("Email Address", validators=
                      [InputRequired(message="Please enter a valid email address"),
                       Email(message="Please enter a valid email address")])

    password=PasswordField("Password", validators=
                         [InputRequired(message="Required"), 
                          Length(min=6, max=20, message="Password must be between 6-20 characters in length")])
    
    password_confirm=PasswordField("Confirm Password", validators=
                                   [InputRequired(message="Required"), 
                                    EqualTo('password', message='Passwords must match')])
    
class LoginForm(FlaskForm):
    """Login form for existing user--username, password"""

    username=StringField("Username", validators=
                         [InputRequired(message="Required")])
    
    password=PasswordField("Password", validators=
                           [InputRequired(message="Required")])