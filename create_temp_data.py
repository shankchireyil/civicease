from flaskblog import db, app,bcrypt
from flaskblog.models import User, Post, Review
import random

indian_states = [
    "Maharashtra",
    "Tamil Nadu",
    "Karnataka",
    "Gujarat",
    "Rajasthan",
    "West Bengal",
    "Uttar Pradesh",
    "Kerala",
    "Punjab",
    "Haryana",
    "Sikkim",
    "Assam",
    "Uttarakhand",
]
indian_psus = [
    "Indian Oil Corporation Limited (IOCL)",
    "State Bank of India (SBI)",
    "Oil and Natural Gas Corporation (ONGC)",
    "Bharat Heavy Electricals Limited (BHEL)",
    "Steel Authority of India Limited (SAIL)",
    "Coal India Limited (CIL)",
    "Indian Railways",
    "Bharat Petroleum Corporation Limited (BPCL)",
    "Hindustan Petroleum Corporation Limited (HPCL)",
    "National Thermal Power Corporation (NTPC)"
]


def create_post():
    with app.app_context():
        for i in range(1, 20):
            rand_no = random.randint(25, 50)
            rand_state = random.choice(indian_states)
            rand_psu = random.choice(indian_psus)

            title = f'Govt job in {rand_psu}'
            content = f'Govt of {rand_state} is offering {rand_no} jobs in {rand_psu}'

            post = Post(title=title, content=content)
            db.session.add(post)

        db.session.commit()


def create_user():

    users = ['shan',"unni", "hari","rohan"]

    with app.app_context():

        for user in users:
            email = f'{user}@gmail.com'
            password = bcrypt.generate_password_hash('pass').decode('utf-8')
            new_user = User(username = user,email= email, password = password)
            db.session.add(new_user)
        db.session.commit()


if __name__ == "__main__":

    with app.app_context():

        db.drop_all()
        db.create_all()
    
    create_user()
    create_post()



