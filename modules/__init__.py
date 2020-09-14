from sqlalchemy import Column, DateTime, String, Boolean
from backend.database import Base
from uuid import uuid5, NAMESPACE_X500
import datetime

__LOREM_STRING__ = ""
__NOT_STARTED__ = "NOT STARTED"
__COMPLETED__ = "COMPLETED"
__IS_COMPLETED__ = False


class Todos(Base):
    __tablename__ = 'todos'
    id = Column(String(50), primary_key=True, unique=True)
    time_created = Column(DateTime(), nullable=False, unique=True)
    task_description = Column(String(120), nullable=False, unique=False, default=__LOREM_STRING__)
    task_status = Column(String(25), nullable=False, unique=False, default=__NOT_STARTED__)
    is_completed = Column(Boolean(), nullable=False, unique=False, default=__IS_COMPLETED__)

    def __init__(self, todo_description):
        self.id = uuid5(NAMESPACE_X500, datetime.datetime.now().ctime()).__str__()
        self.time_created = datetime.datetime.now()
        self.task_status = __NOT_STARTED__
        self.task_description = todo_description
        self.isVisible = __IS_COMPLETED__

    def __repr__(self):
        return '<Todo %r>' % self.id
