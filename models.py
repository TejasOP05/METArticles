from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='author')  # 'author', 'supervisor', 'admin'
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    active_status = db.Column(db.Boolean, default=True)
    
    @property
    def is_active(self):
        """Required by Flask-Login"""
        return self.active_status
    
    # Relationship with articles
    articles = db.relationship('Article', foreign_keys='Article.author_id', backref='author', lazy=True)
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        """Get full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def is_supervisor(self):
        """Check if user is supervisor or admin"""
        return self.role in ['supervisor', 'admin']
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'admin'

class Article(db.Model):
    __tablename__ = 'articles'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    abstract = db.Column(db.Text)
    keywords = db.Column(db.String(500))
    category = db.Column(db.String(100))
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'approved', 'rejected'
    download_count = db.Column(db.Integer, default=0)
    
    # Timestamps
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime)
    
    # Foreign keys
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    reviewer = db.relationship('User', foreign_keys=[reviewer_id])
    
    @property
    def is_approved(self):
        """Check if article is approved"""
        return self.status == 'approved'
    
    @property
    def is_pending(self):
        """Check if article is pending"""
        return self.status == 'pending'
    
    @property
    def is_rejected(self):
        """Check if article is rejected"""
        return self.status == 'rejected'

class ArticleComment(db.Model):
    __tablename__ = 'article_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    article = db.relationship('Article', backref='comments')
    user = db.relationship('User', backref='comments')
