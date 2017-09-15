import bestvods.models as models
import datetime
import flask
import json


def accepts_json(request: flask.request):
    best = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    return best == 'application/json' and request.accept_mimetypes[best] > request.accept_mimetypes['text/html']


def _custom_default(o):
    if isinstance(o, models.Base):
        attrs = {k: v for k, v in o.__dict__.items() if (not k.startswith('_')
                                                         and not k == 'timestamp_modified'
                                                         and not k == 'timestamp_created')}
        return attrs
    elif isinstance(o, datetime.datetime):
        return o.timestamp()
    elif isinstance(o, datetime.date):
        return str(o)
    else:
        return TypeError()


def custom_dumps(o):
    return json.dumps(o, default=_custom_default, sort_keys=True)
