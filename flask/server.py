import sys

from app import create_app, set_db
from app.core.errors import NoConfigError


def run_server(config_name):
    app = create_app(config_name)
    app.app_context().push()
    set_db(app)
    app.run(host=app.config["HOST"], port=app.config["PORT"], debug=app.config["DEBUG"])


if __name__ == "__main__":
    try:
        try:
            run_server(sys.argv[1])
        except IndexError as e:
            raise NoConfigError
    except Exception as e:
        print(e)
