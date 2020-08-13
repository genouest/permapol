from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from app import app

class CreateGroupForm(FlaskForm):
    group_name = StringField("", validators=[DataRequired()])

    def validate_group_name(self, form, field):
        wa = app.config["APOLLO_INSTANCE"]
        if wa.groups.get_groups(field.data):
            raise ValidationError("This group name is already in use")
