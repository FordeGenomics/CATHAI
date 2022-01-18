from flask_wtf import FlaskForm
from wtforms import ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms.fields import (
    PasswordField,
    StringField,
    SubmitField,
    HiddenField
)
from wtforms.fields.html5 import EmailField
from wtforms.validators import (
    Email,
    EqualTo,
    InputRequired,
    Length,
)

from app import db
from app.models import Role, User, Group

class NewGroupForm(FlaskForm):
  name = StringField('Name', validators=[InputRequired(), Length(1, 64)])
  users = QuerySelectMultipleField('Users', query_factory=lambda: db.session.query(User).order_by('first_name'))
  submit = SubmitField('Create')
  

class EditGroupForm(NewGroupForm):  
  submit = SubmitField('Update')


class InviteUserForm(FlaskForm):
    role = QuerySelectField(
        'Account type',
        validators=[InputRequired()],
        get_label='name',
        query_factory=lambda: db.session.query(Role).order_by('permissions'))
    first_name = StringField(
        'First name', validators=[InputRequired(),
                                  Length(1, 64)])
    last_name = StringField(
        'Last name', validators=[InputRequired(),
                                 Length(1, 64)])
    email = EmailField(
        'Email', validators=[InputRequired(),
                             Length(1, 64),
                             Email()])

    groups = QuerySelectMultipleField('Groups', get_label='name', query_factory=lambda: db.session.query(Group).order_by('name')) 

    submit = SubmitField('Invite')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class NewUserForm(InviteUserForm):
    password = PasswordField(
        'Password',
        validators=[
            InputRequired(),
            EqualTo('password2', 'Passwords must match.')
        ])
    password2 = PasswordField('Confirm password', validators=[InputRequired()])

    submit = SubmitField('Create')


class EditUserForm(InviteUserForm):
  uid = HiddenField('id')
  submit = SubmitField('Edit')
  def validate_email(self, field):

    if User.query.filter_by(email=field.data).first():
      print("boopy")
      print(type(User.query.filter_by(email=field.data).first().id))
      print(type(self.uid.data))
      if User.query.filter_by(email=field.data).first().id != int(self.uid.data):
        raise ValidationError('Email already registered.')