from flask_wtf import FlaskForm
from wtforms import TextAreaField
from wtforms.validators import DataRequired

class TweetForm(FlaskForm):
    tweet_text = TextAreaField('ツイート', validators=[DataRequired()])