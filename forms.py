from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, TextAreaField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(), 
        Length(min=4, max=20, message="Username must be between 4 and 20 characters")
    ])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[Length(max=50)])
    last_name = StringField('Last Name', validators=[Length(max=50)])
    password = PasswordField('Password', validators=[
        DataRequired(), 
        Length(min=6, message="Password must be at least 6 characters")
    ])
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(), 
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class ArticleSubmissionForm(FlaskForm):
    title = StringField('Article Title', validators=[
        DataRequired(), 
        Length(max=200, message="Title must be less than 200 characters")
    ])
    abstract = TextAreaField('Abstract', validators=[
        DataRequired(),
        Length(max=2000, message="Abstract must be less than 2000 characters")
    ])
    keywords = StringField('Keywords (comma-separated)', validators=[
        Length(max=500, message="Keywords must be less than 500 characters")
    ])
    category = SelectField('Category', choices=[
        ('computer_science', 'Computer Science'),
        ('engineering', 'Engineering'),
        ('mathematics', 'Mathematics'),
        ('physics', 'Physics'),
        ('chemistry', 'Chemistry'),
        ('biology', 'Biology'),
        ('medicine', 'Medicine'),
        ('social_sciences', 'Social Sciences'),
        ('humanities', 'Humanities'),
        ('business', 'Business'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    file = FileField('PDF File', validators=[
        FileRequired(),
        FileAllowed(['pdf'], 'Only PDF files are allowed!')
    ])
    submit = SubmitField('Submit Article')

class ArticleReviewForm(FlaskForm):
    status = SelectField('Decision', choices=[
        ('approved', 'Approve'),
        ('rejected', 'Reject')
    ], validators=[DataRequired()])
    comment = TextAreaField('Review Comments', validators=[
        Length(max=1000, message="Comments must be less than 1000 characters")
    ])
    submit = SubmitField('Submit Review')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(), 
        Length(min=6, message="Password must be at least 6 characters")
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(), 
        EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Change Password')
