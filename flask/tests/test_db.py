from core.models import Action

# TODO: CHANGE TO TEST DB
def test_post_action(db_session):
    db_session.add(Action("testing1"))
    db_session.commit()


def test_delete_action(db_session):
    db_session.query(Action).filter(Action.name == "testing1").delete()
    db_session.commit()
