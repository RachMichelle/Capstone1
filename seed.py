from app import app
from models import db, User, Inspo

with app.app_context():

    db.drop_all()
    db.create_all()

    u1=User.register_user(username='Bowie', email='b@gmail.com', password='testpassword')
    u2=User.register_user(username='Queen', email='q@email.com', password='testpassword2')

    db.session.add_all([u1, u2])
    db.session.commit()

    i1=Inspo.make_inspo(notes='This is a note', user_id=1)
    i2=Inspo.make_inspo(notes='This is an idea for something', user_id=1)
    i3=Inspo.make_inspo(notes='Here is a note about a thing', user_id=2)

    db.session.add_all([i1, i2, i3])
    db.session.commit()