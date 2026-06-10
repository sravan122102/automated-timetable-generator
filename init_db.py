from app import app, db
from models import User, TimeSlot
from werkzeug.security import generate_password_hash

def init_database():
    with app.app_context():
        # Create all tables
        db.create_all()

        # Check if admin user exists
        if not User.query.filter_by(username='admin').first():
            print("Creating default admin user...")
            admin_user = User(
                username='admin',
                password_hash=generate_password_hash('password123')
            )
            db.session.add(admin_user)
            
        # Check if time slots exist
        if TimeSlot.query.count() == 0:
            print("Creating default time slots...")
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
            periods_per_day = 8
            lunch_period = 5
            
            for day in days:
                for period in range(1, periods_per_day + 1):
                    ts = TimeSlot(
                        day_of_week=day,
                        period_number=period,
                        is_lunch_break=(period == lunch_period)
                    )
                    db.session.add(ts)
        
        db.session.commit()
        print("Database initialization complete.")

if __name__ == '__main__':
    init_database()
