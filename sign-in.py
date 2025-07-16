from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class SignInForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    sex = SelectField('Sex', choices=[('F', 'F'), ('M', 'M')], validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=12)])
    allergies = StringField('Do you have allergies? (y/n)', validators=[DataRequired()])
    conditions = StringField('Do you have conditions? (y/n)', validators=[DataRequired()])
    medications = StringField('Are you on regular medications? (y/n)', validators=[DataRequired()])
    restrictions = StringField('Do you have dietary restrictions? (y/n)', validators=[DataRequired()])
    nutri_goal = StringField('Nutrition goal', validators=[DataRequired()])
    submit = SubmitField('Submit')