#!/usr/bin/env python3
"""
Script to reset user passwords in MetArticles
Usage: python reset_password.py <username> <new_password>
"""

from app import app, db
from models import User
import sys

def reset_password(username, new_password):
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"Error: User '{username}' not found!")
            print("\nAvailable users:")
            users = User.query.all()
            for u in users:
                print(f"  - {u.username} ({u.email}, role: {u.role})")
            return False
        
        user.set_password(new_password)
        db.session.commit()
        print(f"[SUCCESS] Password successfully reset for user: {username}")
        print(f"  Email: {user.email}")
        print(f"  Role: {user.role}")
        print(f"  New password: {new_password}")
        return True

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python reset_password.py <username> <new_password>")
        print("\nExample: python reset_password.py admin mynewpassword")
        sys.exit(1)
    
    username = sys.argv[1]
    new_password = sys.argv[2]
    reset_password(username, new_password)

