from copy import copy
from datetime import datetime

from flask import (Blueprint, render_template, request, make_response,
                   current_app as app)
from werkzeug.utils import secure_filename

from bson import ObjectId
from bson.json_util import dumps, RELAXED_JSON_OPTIONS
from .forms import UploadForm

bp = Blueprint("main", __name__)


@bp.route('/')
def index():
    form = UploadForm()
    return render_template('index.html', form=form)


@bp.route('/themes/')
def themes():
    db = app.mongo.db
    thumbs_up = {'$max': ['$thumbs_up', 0]}
    thumbs_dn = {'$max': ['$thumbs_dn', 0]}
    _score = {'$subtract': [thumbs_up, {'$divide': [thumbs_dn, 2]}]}
    videos = db.videos.aggregate([{'$group': {'_id': '$theme',
                                                    'score': {'$sum': _score},
                                                    'count': {'$sum': 1},
                                                    }}])
    return render_template('themes.html', videos=videos)


@bp.route('/api/upload/', methods=['POST'])
def api_upload():
    form = UploadForm(request.form)
    if form.validate_on_submit():
        coll = app.mongo.db.videos
        data = copy(form.data)
        data['video'] = secure_filename(request.files['video'].filename)
        data['mime_type'] = request.files['video'].content_type
        data['added'] = datetime.utcnow()
        if 'csrf_token' in data:
            del data['csrf_token']
        inserted = coll.insert_one(data)
        obj = coll.find_one({'_id': inserted.inserted_id},
                            ['_id', 'added', 'thumbs_up', 'thumbs_dn',
                             'name', 'theme', 'video'])
        app.mongo.save_file(data['video'], request.files['video'], content_type=data['mime_type'])
        return dumps(obj, json_options=RELAXED_JSON_OPTIONS)
    else:
        return form.errors, 400


@bp.route('/api/videos/', methods=['GET'])
def api_videos():
    db = app.mongo.db
    docs = db.videos.find({}, ['_id', 'added', 'thumbs_up', 'thumbs_dn',
                                     'name', 'theme', 'video', 'mime_type'])
    response = make_response(dumps([doc for doc in docs],
                                   json_options=RELAXED_JSON_OPTIONS), 200)
    response.headers['Content-Type'] = 'application/json'
    return response


@bp.route('/api/thumbs/<ObjectId:vid>/', methods=['PUT'])
def api_thumbs(vid):
    data = request.json
    db = app.mongo.db
    ur = db.videos.find_one_and_update({'_id': vid},
                                       {'$inc': {'thumbs_%s' % data['dir']: 1}})

    response = make_response(dumps(ur, json_options=RELAXED_JSON_OPTIONS), 200)
    response.headers['Content-Type'] = 'application/json'
    return response


@bp.route('/download/<path:filename>/', methods=['GET'])
def download(filename):
    video = app.mongo.send_file(filename)
    response = make_response(video, 200)
    response.headers['Content-type'] = 'video/mpeg'
    return response
