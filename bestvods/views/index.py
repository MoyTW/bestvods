import flask

blueprint = flask.Blueprint('index', __name__, template_folder='templates')


@blueprint.route('/', methods=['GET'])
def root():
    return flask.render_template('index.html')
