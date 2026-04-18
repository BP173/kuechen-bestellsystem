from app import create_app, db
from app.models import User, TargetDepartment

app = create_app()

with app.app_context():
    db.session.add_all([
        User(name="Max", department="Küche"),
        User(name="Anna", department="Patisserie")
    ])

    db.session.add_all([
        TargetDepartment(name="Frühstück"),
        TargetDepartment(name="Bankett"),
        TargetDepartment(name="À la carte")
    ])

    db.session.commit()