import datetime
import sqlite3
import flask_testing
import bestvods.main as app

test_config = {
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + app.ROOT_DIR + '/../dev/test.db',
    'TESTING': True
}


def timestamp_almost_now(timestamp):
    now = datetime.datetime.utcnow()
    dt_timestamp = datetime.datetime.strptime(timestamp,  "%Y-%m-%d %H:%M:%S")
    return now - datetime.timedelta(seconds=5) < dt_timestamp < now + datetime.timedelta(seconds=5)


class BaseQueryTest(flask_testing.TestCase):
    def create_app(self):
        return app.create_app(test_config)

    def setUp(self):
        with open(app.ROOT_DIR + '/../dev/schema.sql', 'r') as schema_file:
            schema = schema_file.read()
        conn = sqlite3.connect(app.ROOT_DIR + '/../dev/test.db')
        conn.executescript(schema)

    def tearDown(self):
        app.db.session.remove()
        app.db.drop_all()
