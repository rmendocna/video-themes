from flask_wtf import FlaskForm
from wtforms import validators
from wtforms.fields import StringField
from flask_wtf.file import FileField, FileRequired, FileAllowed

EXTENSIONS = ['mkv', 'avi', 'mpg', 'mov']


class UploadForm(FlaskForm):
    name = StringField(u'Name', validators=[validators.input_required()])
    theme = StringField(u'Theme', validators=[validators.input_required()])
    video = FileField(u'File',
                      validators=[# FileRequired(),
                                  FileAllowed(EXTENSIONS)
                                  ], render_kw=dict(accept='video/*'))
