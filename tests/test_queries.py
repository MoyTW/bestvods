import datetime
import sqlite3
import flask_testing
import bestvods.main as app
import bestvods.queries as queries

test_config = {
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + app.ROOT_DIR + '/../dev/test.db',
    'TESTING': True
}


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


class InsertGameTest(BaseQueryTest):
    @staticmethod
    def test_game_inserts_once():
        queries.insert_game(app.db, 'n', 2004, 'The original')
        result = app.db.engine.execute('select * from game').fetchall()
        assert result[0] == ('n', 2004, 'The original')
        assert len(result) == 1

    @staticmethod
    def test_game_inserts_only_once():
        queries.insert_game(app.db, 'n', 2004, 'The original')
        queries.insert_game(app.db, 'n', 2004, 'The original')
        result = app.db.engine.execute('select * from game').fetchall()
        assert len(result) == 1

    @staticmethod
    def test_game_inserts_multiple():
        queries.insert_game(app.db, 'n', 2004, 'The original')
        queries.insert_game(app.db, 'n+', 2008, 'The sequel')
        queries.insert_game(app.db, 'n++', 2015, 'Not a programming language surprisingly')
        result = app.db.engine.execute('select * from game').fetchall()
        assert result[2] == ('n++', 2015, 'Not a programming language surprisingly')
        assert len(result) == 3

    @staticmethod
    def test_differentiates_by_year():
        queries.insert_game(app.db, 'Doom', 1993, 'Old')
        queries.insert_game(app.db, 'Doom', 2016, 'New')
        result = app.db.engine.execute('select * from game').fetchall()
        assert result[0] == ('Doom', 1993, 'Old')
        assert result[1] == ('Doom', 2016, 'New')
        assert len(result) == 2


class InsertCategoryTest(BaseQueryTest):
    @staticmethod
    def test_category_inserts_once():
        queries.insert_category(app.db, 'Any%', 'Finish by any means possible')
        result = app.db.engine.execute('select * from category').fetchall()
        assert result[0] == ('Any%', 'Finish by any means possible')
        assert len(result) == 1

    @staticmethod
    def test_category_inserts_only_once():
        queries.insert_category(app.db, 'Any%', 'Finish by any means possible')
        queries.insert_category(app.db, 'Any%', 'Finish by any means possible')
        result = app.db.engine.execute('select * from category').fetchall()
        assert len(result) == 1

    @staticmethod
    def test_category_inserts_multiple():
        queries.insert_category(app.db, 'Any%', 'Finish by any means possible')
        queries.insert_category(app.db, '100%', 'Get everything')
        queries.insert_category(app.db, 'low%', 'Finish with the minimum possible')
        result = app.db.engine.execute('select * from category').fetchall()
        assert result[2] == ('low%', 'Finish with the minimum possible')
        assert len(result) == 3


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
