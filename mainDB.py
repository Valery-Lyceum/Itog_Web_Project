from flask import Flask
from data import db_session
from data.users import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


def nomain(cmd, polz, nazv='', pt=0):
    db_session.global_init("db/blogs.db")
    if cmd == "add":
        user = User()
        user.name = polz
        user.title = nazv
        user.points = pt
        db_sess = db_session.create_session()
        db_sess.add(user)
        db_sess.commit()
    elif cmd == "del":
        db_sess = db_session.create_session()
        db_sess.query(User).filter(User.name == polz, User.title == nazv).delete()
        db_sess.commit()
    elif cmd == "see":
        db_sess = db_session.create_session()
        olmps = []
        for olmp in db_sess.query(User).filter(User.name == polz):
            olmps.append([olmp.title, olmp.points])
        return olmps