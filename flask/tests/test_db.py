from core.models import Action, Location, TodoParent, TodoChildren

from datetime import datetime
from dateutil.relativedelta import relativedelta


def test_check_if_tables_created(db_engine, tables):
    assert Action.__tablename__ in db_engine.table_names()
    assert Location.__tablename__ in db_engine.table_names()
    assert TodoParent.__tablename__ in db_engine.table_names()
    assert TodoChildren.__tablename__ in db_engine.table_names()


def test_post_action(db_session, tables):
    db_session.add(Action("testing-action"))
    db_session.commit()


def test_delete_action(db_session, tables):
    db_session.query(Action).filter(Action.name == "testing-action").delete()
    db_session.commit()


def test_post_location(db_session, tables):
    db_session.add(Location("testing-location"))
    db_session.commit()


def test_delete_action(db_session, tables):
    db_session.query(Location).filter(Location.name == "testing-location").delete()
    db_session.commit()


def test_create_todo_parent(db_session, tables):
    now = datetime.now()
    db_session.add(
        TodoParent(
            "Have a bath",
            "1m",
            now,
            now + relativedelta(months=6),
        )
    )
    db_session.commit()


def test_delete_todo_parent(db_session, tables):
    now = datetime.now()
    db_session.add(
        TodoParent(
            "Take medicine",
            "1m",
            now,
            now + relativedelta(months=6),
        )
    )
    db_session.query(TodoParent).filter(TodoParent.task == "Take medicine").delete()
    db_session.commit()


def test_create_todo_children(db_session, tables):
    now = datetime.now()
    todo_parent = (
        db_session.query(TodoParent).filter(TodoParent.task == "Have a bath").first()
    )
    db_session.add(TodoChildren(now, todo_parent.id))
    db_session.commit()
