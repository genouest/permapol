import re

from flask import current_app

from flask_wtf import FlaskForm

from wtforms import StringField
from wtforms.validators import DataRequired, ValidationError


class CreateGroupForm(FlaskForm):
    group_name = StringField("Group name", validators=[DataRequired()])

    def validate_group_name(form, field):

        if not re.match('^[a-zA-Z0-9_]+$', field.data):
            raise ValidationError("Use only letters, digits or underscore")

        wa = current_app.config["APOLLO_INSTANCE"]
        if wa.groups.get_groups(field.data):
            raise ValidationError("This group name is already in use")


class AddUserForm(FlaskForm):
    user_mail = StringField("User email", validators=[DataRequired()])

    def validate_user_mail(form, field):
        wa = current_app.config["APOLLO_INSTANCE"]

        if not wa.users.show_user(field.data):
            raise ValidationError("This user is not registered in Apollo")
