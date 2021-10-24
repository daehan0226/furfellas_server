from core.models import Action


def test_check_if_tables_created(db_engine, tables):
    assert Action.__tablename__ in db_engine.table_names()


def test_post_action(db_session, tables):
    db_session.add(Action("testing1"))
    db_session.commit()


def test_delete_action(db_session, tables):
    db_session.query(Action).filter(Action.name == "testing1").delete()
    db_session.commit()
