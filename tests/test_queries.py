import datetime
import sqlite3
import flask_testing
import bestvods.main as app
import bestvods.queries as queries

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


class InsertPlatformTest(BaseQueryTest):
    @staticmethod
    def test_platform_inserts_once():
        queries.insert_platform(app.db, 'NES', 'Nintendo Entertainment System')
        result = app.db.engine.execute('select * from platform').fetchall()
        assert result[0] == ('NES', 'Nintendo Entertainment System')
        assert len(result) == 1

    @staticmethod
    def test_platform_inserts_only_once():
        queries.insert_platform(app.db, 'NES', 'Nintendo Entertainment System')
        queries.insert_platform(app.db, 'NES', 'Nintendo Entertainment System')
        result = app.db.engine.execute('select * from platform').fetchall()
        assert len(result) == 1

    @staticmethod
    def test_platform_inserts_multiple():
        queries.insert_platform(app.db, 'NES', 'Nintendo Entertainment System')
        queries.insert_platform(app.db, 'SNES', 'Super Nintendo Entertainment System')
        queries.insert_platform(app.db, 'N64', 'Nintendo 64')
        result = app.db.engine.execute('select * from platform').fetchall()
        assert result[2] == ('N64', 'Nintendo 64')
        assert len(result) == 3


class InsertEventTest(BaseQueryTest):
    @staticmethod
    def test_event_inserts_once():
        queries.insert_event(app.db, '2k', datetime.date(2000, 1, 1), datetime.date(2000, 1, 2), 'e2k')
        result = app.db.engine.execute('select * from event').fetchall()
        assert result[0] == ('2k', '2000-01-01', '2000-01-02', 'e2k')
        assert len(result) == 1

    @staticmethod
    def test_event_inserts_only_once():
        queries.insert_event(app.db, '2k', datetime.date(2000, 1, 1), datetime.date(2000, 1, 2), 'e2k')
        queries.insert_event(app.db, '2k', datetime.date(2000, 1, 1), datetime.date(2000, 1, 2), 'e2k')
        result = app.db.engine.execute('select * from event').fetchall()
        assert len(result) == 1

    @staticmethod
    def test_event_inserts_multiple():
        queries.insert_event(app.db, '2k', datetime.date(2000, 1, 1), datetime.date(2000, 1, 2), 'e2k')
        queries.insert_event(app.db, '2k1', datetime.date(2001, 1, 1), datetime.date(2001, 1, 2), 'e2k1')
        queries.insert_event(app.db, '2k2', datetime.date(2002, 1, 1), datetime.date(2002, 1, 2), 'e2k2')
        result = app.db.engine.execute('select * from event').fetchall()
        assert result[2] == ('2k2', '2002-01-01', '2002-01-02', 'e2k2')
        assert len(result) == 3
