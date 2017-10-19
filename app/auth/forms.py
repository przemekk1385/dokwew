from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired, EqualTo

from ..models import User


class RegistrationForm(FlaskForm):
    username = StringField('Nazwa użytkownika', validators=[DataRequired()])
    password = PasswordField('Hasło', validators=[DataRequired(),
                             EqualTo('confirm_password')])
    confirm_password = PasswordField('Potwierdź hasło')
    submit = SubmitField('Zarejestruj')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Użytkownik o podanej nazwie' +
                                  'już istnieje!')


class LoginForm(FlaskForm):
    username = StringField('Użytkownik', validators=[DataRequired()])
    password = PasswordField('Hasło', validators=[DataRequired()])
    submit = SubmitField('Zaloguj')
