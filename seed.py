from app import app
from models import db, User

with app.app_context():

    db.drop_all()
    db.create_all()

    u1=User.register_user(username='Bowie', email='b@gmail.com', password='testpassword')
    u2=User.register_user(username='Queen', email='q@email.com', password='testpassword2')

    db.session.add_all([u1, u2])
    db.session.commit()