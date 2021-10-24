from core.models.action import Action
from core.models.location import Location


def test_check_if_tables_created(db_engine, tables):
    assert Action.__tablename__ in db_engine.table_names()
    assert Location.__tablename__ in db_engine.table_names()


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
