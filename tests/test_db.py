import sqlite3
import flask_testing
import bestvods.main as app
import bestvods.db as db

test_config = {
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + app.ROOT_DIR + '/test.db',
    'TESTING': True
}


class BaseDBTest(flask_testing.TestCase):
    def create_app(self):
        return app.create_app(test_config)

    def setUp(self):
        with open(app.ROOT_DIR + '/schema.sql', 'r') as schema_file:
            schema = schema_file.read()
        conn = sqlite3.connect(app.ROOT_DIR + '/test.db')
        conn.executescript(schema)

    def tearDown(self):
        app.db.session.remove()
        app.db.drop_all()


class InsertGameTest(BaseDBTest):
    @staticmethod
    def test_game_inserts_once():
        db.insert_game(app.db, 'n', 2004, 'The original')
        result = app.db.engine.execute('select * from game').fetchall()
        assert result[0] == ('n', 2004, 'The original')
        assert len(result) == 1

    @staticmethod
    def test_game_inserts_only_once():
        db.insert_game(app.db, 'n', 2004, 'The original')
        db.insert_game(app.db, 'n', 2004, 'The original')
        result = app.db.engine.execute('select * from game').fetchall()
        assert len(result) == 1

    @staticmethod
    def test_game_inserts_multiple():
        db.insert_game(app.db, 'n', 2004, 'The original')
        db.insert_game(app.db, 'n+', 2008, 'The sequel')
        db.insert_game(app.db, 'n++', 2015, 'Not a programming language surprisingly')
        result = app.db.engine.execute('select * from game').fetchall()
        assert result[2] == ('n++', 2015, 'Not a programming language surprisingly')
        assert len(result) == 3

    @staticmethod
    def test_differentiates_by_year():
        db.insert_game(app.db, 'Doom', 1993, 'Old')
        db.insert_game(app.db, 'Doom', 2016, 'New')
        result = app.db.engine.execute('select * from game').fetchall()
        assert result[0] == ('Doom', 1993, 'Old')
        assert result[1] == ('Doom', 2016, 'New')
        assert len(result) == 2


class InsertCategoryTest(BaseDBTest):
    @staticmethod
    def test_category_inserts_once():
        db.insert_category(app.db, 'Any%', 'Finish by any means possible')
        result = app.db.engine.execute('select * from category').fetchall()
        assert result[0] == ('Any%', 'Finish by any means possible')
        assert len(result) == 1

    @staticmethod
    def test_category_inserts_only_once():
        db.insert_category(app.db, 'Any%', 'Finish by any means possible')
        db.insert_category(app.db, 'Any%', 'Finish by any means possible')
        result = app.db.engine.execute('select * from category').fetchall()
        assert len(result) == 1

    @staticmethod
    def test_category_inserts_multiple():
        db.insert_category(app.db, 'Any%', 'Finish by any means possible')
        db.insert_category(app.db, '100%', 'Get everything')
        db.insert_category(app.db, 'low%', 'Finish with the minimum possible')
        result = app.db.engine.execute('select * from category').fetchall()
        assert result[2] == ('low%', 'Finish with the minimum possible')
        assert len(result) == 3


class InsertPlatformTest(BaseDBTest):
    @staticmethod
    def test_platform_inserts_once():
        db.insert_platform(app.db, 'NES', 'Nintendo Entertainment System')
        result = app.db.engine.execute('select * from platform').fetchall()
        assert result[0] == ('NES', 'Nintendo Entertainment System')
        assert len(result) == 1

    @staticmethod
    def test_platform_inserts_only_once():
        db.insert_platform(app.db, 'NES', 'Nintendo Entertainment System')
        db.insert_platform(app.db, 'NES', 'Nintendo Entertainment System')
        result = app.db.engine.execute('select * from platform').fetchall()
        assert len(result) == 1

    @staticmethod
    def test_platform_inserts_multiple():
        db.insert_platform(app.db, 'NES', 'Nintendo Entertainment System')
        db.insert_platform(app.db, 'SNES', 'Super Nintendo Entertainment System')
        db.insert_platform(app.db, 'N64', 'Nintendo 64')
        result = app.db.engine.execute('select * from platform').fetchall()
        assert result[2] == ('N64', 'Nintendo 64')
        assert len(result) == 3
