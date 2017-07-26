import sqlite3
import flask_testing
import bestvods.main as app
import bestvods.db as db

test_config = {
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + app.ROOT_DIR + '/test.db',
    'TESTING': True
}


class MyTest(flask_testing.TestCase):
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

    def test_game_inserts_once(self):
        db.insert_game(app.db, 'n', 2017, 'test desc')
        result = app.db.engine.execute('select * from game').fetchall()
        assert result[0] == ('n', 2017, 'test desc')
        assert len(result) == 1
