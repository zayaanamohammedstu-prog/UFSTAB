#!/bin/bash
# Database initialization and migration script

echo "OratorHub Database Setup"
echo "========================"

# Set default environment
export FLASK_APP=app.py
export FLASK_ENV=${FLASK_ENV:-development}

echo "Environment: $FLASK_ENV"

# Initialize migrations if not exists
if [ ! -d "migrations" ]; then
    echo "Initializing database migrations..."
    flask db init
fi

# Create migration
echo "Creating migration..."
flask db migrate -m "Initial migration"

# Apply migration
echo "Applying migration..."
flask db upgrade

# Create default admin user (only in development)
if [ "$FLASK_ENV" = "development" ]; then
    echo "Creating default admin user..."
    python - <<EOF
from app import create_app
from models import db, User

app = create_app()
with app.app_context():
    # Check if admin exists
    admin = User.query.filter_by(email='admin@oratorhub.com').first()
    if not admin:
        admin = User(
            email='admin@oratorhub.com',
            username='admin',
            full_name='Admin User',
            role='admin',
            is_active=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Admin user created: admin@oratorhub.com / admin123")
    else:
        print("Admin user already exists")
EOF
fi

echo "Database setup complete!"
