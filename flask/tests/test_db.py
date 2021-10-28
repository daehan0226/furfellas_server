import sqlalchemy
from core.models import Action, Location, TodoParent, TodoChildren


def test_check_if_tables_created(db_engine):
    insp = sqlalchemy.inspect(db_engine)
    assert insp.dialect.has_table(db_engine.connect(), Action.__tablename__)
    assert insp.dialect.has_table(db_engine.connect(), Location.__tablename__)
    assert insp.dialect.has_table(db_engine.connect(), TodoParent.__tablename__)
    assert insp.dialect.has_table(db_engine.connect(), TodoChildren.__tablename__)
