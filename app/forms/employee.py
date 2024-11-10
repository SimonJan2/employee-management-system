from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, DecimalField, FileField
from wtforms.validators import DataRequired, Email, Optional

class EmployeeForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    department_id = SelectField('Department', coerce=str, validators=[DataRequired()])
    position = StringField('Position', validators=[DataRequired()])
    hire_date = DateField('Hire Date', validators=[DataRequired()])
    salary = DecimalField('Salary', validators=[Optional()])
    profile_picture = FileField('Profile Picture')