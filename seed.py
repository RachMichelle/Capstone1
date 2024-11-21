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
    i4=Inspo.make_inspo(has_favorite=True, image="https://images.metmuseum.org/CRDImages/as/original/DP251139.jpg", name="Hanging scroll", artist="Kiyohara Yukinobu", medium="Hanging scroll; ink and color on silk", dimensions="46 5/8 x 18 3/4 in. (118.4 x 47.6 cm)", creation_date="late 17th century", notes="user note about piece", user_id=2)

    db.session.add_all([i1, i2, i3, i4])
    db.session.commit()