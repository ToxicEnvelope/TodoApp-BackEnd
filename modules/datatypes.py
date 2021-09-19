import jwt
import datetime
from sqlalchemy import Column, DateTime, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base
from uuid import uuid5, NAMESPACE_X500


__LOREM_STRING__ = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
__NOT_STARTED__ = "NOT STARTED"
__COMPLETED__ = "COMPLETED"
__IS_COMPLETED__ = False


class Users(Base):
    __tablename__ = 'users'
    id = Column(String(50), primary_key=True)
    name = Column(String(50), unique=False, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(120), unique=True)
    created_time = Column(DateTime(), nullable=False)
    modified_time = Column(DateTime(), nullable=False)
    token = Column(String(256), unique=True, nullable=True)
    todos = relationship('Todos', backref='task_to_user', cascade='all,delete')

    def __init__(self, name=None, email=None, passwd=None):
        self.name = name
        self.email = email
        self.password = passwd
        self.created_time = datetime.datetime.now()
        self.modified_time = datetime.datetime.now()
        self.id = uuid5(NAMESPACE_X500, f'{self.name}-{self.created_time}').__str__()

    def __repr__(self):
        return '<User %r>' % self.id

    @staticmethod
    def encode_auth_token(user_id, seconds=600):
        payload = {
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=seconds),
            "iat": datetime.datetime.utcnow(),
            "sub": user_id
        }
        return jwt.encode(
            payload=payload,
            key='d032c84b34cdb5b061af09151a758688bc732371',
            algorithm="HS256"
        )


class Todos(Base):
    __tablename__ = 'todos'
    id = Column(String(50), primary_key=True, unique=True)
    user_id = Column(String, ForeignKey('users.id'))
    time_created = Column(DateTime(), nullable=False, unique=True)
    task_description = Column(String(120), nullable=False, unique=False, default=__LOREM_STRING__)
    task_status = Column(String(25), nullable=False, unique=False, default=__NOT_STARTED__)
    is_completed = Column(Boolean(), nullable=False, unique=False, default=__IS_COMPLETED__)

    def __init__(self, description=None, user_id=None):
        self.user_id = user_id
        self.id = uuid5(NAMESPACE_X500, f'{self.user_id}-{datetime.datetime.now().ctime()}').__str__()
        self.time_created = datetime.datetime.now()
        self.task_status = __NOT_STARTED__
        self.task_description = description
        self.isVisible = __IS_COMPLETED__

    def __repr__(self):
        return '<Todo %r>' % self.id
