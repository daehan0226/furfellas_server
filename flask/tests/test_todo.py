from core.models.todo import TodoParent
from resources.todos import get_todos
from datetime import datetime
from dateutil.relativedelta import relativedelta

def test_get_todos():
    todos = get_todos()
    assert isinstance(todos, list) 

def test_get_todo_by_id():
    id = 1
    todo = get_todos(id=id)
    assert todo["id"] == id


def test_create_todo_parent(db_session, tables):
    now = datetime.now()
    db_session.add(TodoParent("Take medicine","1m", now, now + relativedelta(months=6),))
    db_session.commit()


# def test_get_todo_parent(db_session, tables):
#     now = datetime.now()
#     db_session.add(TodoParent("Have a bath","2m", now, now + relativedelta(months=6),))
#     db_session.commit()

#     todo = db_session.query(TodoParent).filter(TodoParent.task=="Have a bath").first()
#     assert todo["repeat_interval"] == "2m"


