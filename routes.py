import os
from flask import render_template, request, redirect, url_for, flash, send_from_directory, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
from sqlalchemy import desc

from app import app, db
from models import User, Article, ArticleComment
from forms import RegistrationForm, LoginForm, ArticleSubmissionForm, ArticleReviewForm, ChangePasswordForm
from utils import save_article_file, get_file_size, format_file_size

@app.route('/')
def index():
    """Home page"""
    # Get trending articles (top 5 by download count)
    trending_articles = Article.query.filter_by(status='approved')\
        .order_by(desc(Article.download_count))\
        .limit(5).all()
    
    # Get recent articles
    recent_articles = Article.query.filter_by(status='approved')\
        .order_by(desc(Article.submitted_at))\
        .limit(3).all()
    
    # Get total counts for statistics
    total_articles = Article.query.filter_by(status='approved').count()
    total_authors = User.query.filter_by(role='author').count()
    
    return render_template('index.html', 
                         trending_articles=trending_articles,
                         recent_articles=recent_articles,
                         total_articles=total_articles,
                         total_authors=total_authors)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            role='author'  # Default role
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data) and user.is_active:
            login_user(user)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.full_name}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/submit-article', methods=['GET', 'POST'])
@login_required
def submit_article():
    """Submit new article (Authors only)"""
    if current_user.role not in ['author', 'admin']:
        flash('You do not have permission to submit articles.', 'error')
        return redirect(url_for('index'))
    
    form = ArticleSubmissionForm()
    if form.validate_on_submit():
        # Save the uploaded file
        filename = save_article_file(form.file.data)
        if filename:
            article = Article(
                title=form.title.data,
                abstract=form.abstract.data,
                keywords=form.keywords.data,
                category=form.category.data,
                filename=filename,
                original_filename=form.file.data.filename,
                file_size=get_file_size(filename),
                author_id=current_user.id
            )
            
            db.session.add(article)
            db.session.commit()
            
            flash('Article submitted successfully! It will be reviewed by our team.', 'success')
            return redirect(url_for('my_articles'))
        else:
            flash('Error saving file. Please try again.', 'error')
    
    return render_template('submit_article.html', form=form)

@app.route('/my-articles')
@login_required
def my_articles():
    """View user's own articles"""
    if current_user.role not in ['author', 'admin']:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    articles = Article.query.filter_by(author_id=current_user.id)\
        .order_by(desc(Article.submitted_at)).all()
    
    return render_template('my_articles.html', articles=articles)

@app.route('/articles')
def articles():
    """List all approved articles"""
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    
    query = Article.query.filter_by(status='approved')
    
    if category:
        query = query.filter_by(category=category)
    
    if search:
        query = query.filter(Article.title.contains(search) | 
                           Article.abstract.contains(search) |
                           Article.keywords.contains(search))
    
    articles = query.order_by(desc(Article.submitted_at))\
        .paginate(page=page, per_page=10, error_out=False)
    
    # Get categories for filter
    categories = db.session.query(Article.category)\
        .filter_by(status='approved')\
        .distinct().all()
    categories = [cat[0] for cat in categories if cat[0]]
    
    return render_template('articles.html', 
                         articles=articles,
                         categories=categories,
                         current_category=category,
                         search=search)

@app.route('/article/<int:id>')
def article_detail(id):
    """Article detail page"""
    article = Article.query.get_or_404(id)
    
    # Only show approved articles to non-supervisors
    if not article.is_approved and not (current_user.is_authenticated and current_user.is_supervisor()):
        abort(404)
    
    return render_template('article_detail.html', article=article)

@app.route('/download/<int:id>')
def download_article(id):
    """Download article file"""
    article = Article.query.get_or_404(id)
    
    # Only allow download of approved articles
    if not article.is_approved:
        abort(404)
    
    # Increment download count
    article.download_count += 1
    db.session.commit()
    
    return send_from_directory(app.config['UPLOAD_FOLDER'], 
                             article.filename,
                             as_attachment=True,
                             download_name=article.original_filename)

@app.route('/preview/<int:id>')
def preview_article(id):
    """Preview article file inline"""
    article = Article.query.get_or_404(id)
    
    # Allow preview of approved articles, or any article for supervisors
    if not article.is_approved and not (current_user.is_authenticated and current_user.is_supervisor()):
        abort(404)
    
    # Security: Only allow PDF files for preview
    if not article.filename.lower().endswith('.pdf'):
        abort(404)
    
    # Serve PDF for inline viewing with security headers
    response = send_from_directory(app.config['UPLOAD_FOLDER'], 
                                 article.filename,
                                 as_attachment=False,
                                 mimetype='application/pdf')
    
    # Add security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Content-Disposition'] = f'inline; filename="{article.original_filename}"'
    
    return response

@app.route('/approval-dashboard')
@login_required
def approval_dashboard():
    """Dashboard for supervisors to review articles"""
    if not current_user.is_supervisor():
        flash('Access denied. Supervisor privileges required.', 'error')
        return redirect(url_for('index'))
    
    # Get pending articles
    pending_articles = Article.query.filter_by(status='pending')\
        .order_by(Article.submitted_at).all()
    
    # Get recently reviewed articles
    reviewed_articles = Article.query.filter(Article.status.in_(['approved', 'rejected']))\
        .order_by(desc(Article.reviewed_at))\
        .limit(10).all()
    
    return render_template('approval_dashboard.html',
                         pending_articles=pending_articles,
                         reviewed_articles=reviewed_articles)

@app.route('/review-article/<int:id>', methods=['GET', 'POST'])
@login_required
def review_article(id):
    """Review article (Supervisors only)"""
    if not current_user.is_supervisor():
        flash('Access denied. Supervisor privileges required.', 'error')
        return redirect(url_for('index'))
    
    article = Article.query.get_or_404(id)
    form = ArticleReviewForm()
    
    if form.validate_on_submit():
        article.status = form.status.data
        article.reviewer_id = current_user.id
        article.reviewed_at = datetime.utcnow()
        
        # Add comment if provided
        if form.comment.data:
            comment = ArticleComment(
                article_id=article.id,
                user_id=current_user.id,
                comment=form.comment.data
            )
            db.session.add(comment)
        
        db.session.commit()
        
        status_text = 'approved' if form.status.data == 'approved' else 'rejected'
        flash(f'Article "{article.title}" has been {status_text}.', 'success')
        return redirect(url_for('approval_dashboard'))
    
    return render_template('review_article.html', article=article, form=form)

@app.route('/user-management')
@login_required
def user_management():
    """User management page for supervisors to promote authors"""
    if not current_user.is_supervisor():
        flash('Access denied. Supervisor privileges required.', 'error')
        return redirect(url_for('index'))
    
    # Get all authors (users with role 'author')
    authors = User.query.filter_by(role='author').order_by(User.created_at.desc()).all()
    
    # Get all supervisors for reference
    supervisors = User.query.filter(User.role.in_(['supervisor', 'admin'])).order_by(User.username).all()
    
    return render_template('user_management.html', authors=authors, supervisors=supervisors)

@app.route('/promote-user/<int:user_id>', methods=['POST'])
@login_required
def promote_user(user_id):
    """Promote an author to supervisor role"""
    if not current_user.is_supervisor():
        flash('Access denied. Supervisor privileges required.', 'error')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    
    if user.role != 'author':
        flash('Only authors can be promoted to supervisor.', 'error')
        return redirect(url_for('user_management'))
    
    # Promote to supervisor
    user.role = 'supervisor'
    db.session.commit()
    
    flash(f'Successfully promoted {user.full_name} to supervisor role.', 'success')
    return redirect(url_for('user_management'))

@app.route('/demote-user/<int:user_id>', methods=['POST'])
@login_required
def demote_user(user_id):
    """Demote a supervisor back to author role (only admins can do this)"""
    if not current_user.is_admin():
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    
    # Prevent demoting the current user
    if user.id == current_user.id:
        flash('You cannot demote yourself.', 'error')
        return redirect(url_for('user_management'))
    
    if user.role not in ['supervisor', 'admin']:
        flash('User is not a supervisor or admin.', 'error')
        return redirect(url_for('user_management'))
    
    # Demote to author
    user.role = 'author'
    db.session.commit()
    
    flash(f'Successfully demoted {user.full_name} to author role.', 'success')
    return redirect(url_for('user_management'))

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user password"""
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        # Verify current password
        if not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect.', 'error')
            return render_template('change_password.html', form=form)
        
        # Check if new password is different from current
        if current_user.check_password(form.new_password.data):
            flash('New password must be different from current password.', 'error')
            return render_template('change_password.html', form=form)
        
        # Update password
        current_user.set_password(form.new_password.data)
        db.session.commit()
        
        flash('Password changed successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('change_password.html', form=form)

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@app.context_processor
def utility_processor():
    """Template utility functions"""
    return dict(format_file_size=format_file_size)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
