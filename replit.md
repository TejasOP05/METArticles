# Overview

MET Articles is a Flask-based academic research article submission and review platform. It serves as a repository where researchers, students, and educators can submit academic papers, have them undergo peer review by supervisors, and share approved research with the broader academic community. The platform provides role-based access control with authors submitting articles, supervisors reviewing submissions, and admins managing the overall system.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Web Framework
The application uses Flask as the core web framework with a traditional MVC architecture. The main application is configured in `app.py` with routes defined in `routes.py`, data models in `models.py`, and forms handled through `forms.py`. The application uses Jinja2 templating engine for rendering HTML pages stored in the `templates/` directory.

## Database Layer
The system uses SQLAlchemy as the ORM with Flask-SQLAlchemy integration. The database models define a User entity with role-based permissions (author, supervisor, admin) and an Article entity with submission status tracking. The database is configured to use connection pooling with automatic reconnection handling for production deployment.

## Authentication & Authorization
Flask-Login handles user session management with password hashing implemented via Werkzeug's security utilities. The system implements a three-tier role system: authors can submit articles, supervisors can review and approve/reject submissions, and admins have full system access. Login state is managed through secure sessions.

## File Management
Article files are handled through a secure upload system that generates random filenames to prevent conflicts and unauthorized access. The system validates file types (PDF only), manages file size limits (16MB max), and stores uploaded files in a dedicated uploads directory outside the web root.

## Frontend Architecture
The user interface uses Bootstrap 5 for responsive design with custom CSS enhancements. JavaScript functionality is centralized in `main.js` for client-side form validation, file upload enhancements, and interactive features. The template system uses a base layout with block inheritance for consistent page structure.

## Review Workflow
The platform implements a formal peer review process where submitted articles start in a "pending" state, supervisors can review and provide feedback through a dedicated dashboard, and articles transition to "approved" or "rejected" states. The system tracks review history and allows for supervisor comments on submissions.

# External Dependencies

## Core Framework Dependencies
- Flask web framework for application structure
- SQLAlchemy/Flask-SQLAlchemy for database operations and ORM
- Flask-Login for user authentication and session management
- Flask-WTF for form handling and CSRF protection
- WTForms for form validation and rendering

## Frontend Dependencies
- Bootstrap 5 CSS framework for responsive UI design
- Font Awesome icon library for consistent iconography
- Custom CSS and JavaScript for enhanced user experience

## Security & Utilities
- Werkzeug for password hashing and secure filename handling
- Python secrets module for generating secure random filenames
- ProxyFix middleware for deployment behind reverse proxies

## Database Configuration
The application is configured to work with any SQLAlchemy-compatible database through environment variables. Connection pooling and automatic ping functionality are configured for production reliability.

## File Storage
Local file system storage for uploaded PDF documents with secure filename generation and directory management. The system creates upload directories automatically and handles file size validation.