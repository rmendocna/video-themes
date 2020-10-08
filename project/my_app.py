from copy import copy
from datetime import datetime

from flask import Flask, render_template, request, make_response
from flask_pymongo import PyMongo
from flask_wtf.csrf import CSRFProtect
from werkzeug.utils import secure_filename

from bson import ObjectId
from bson.json_util import dumps, RELAXED_JSON_OPTIONS
from .forms import UploadForm


app = Flask(__name__)
app.config.update(dict(
    TEST=True,
    SECRET_KEY='zY0ZI4BtQ50OuZBftm6ckA',
    MONGO_URI="mongodb://localhost:27017/moviethemes",
    STATIC_FOLDER='./static'
))
mongo = PyMongo(app)
csrf = CSRFProtect(app)


@app.route('/')
def index():
    form = UploadForm()
    return render_template('index.html', form=form)


@app.route('/api/upload/', methods=['POST'])
def api_upload():
    form = UploadForm(request.form)
    if form.validate_on_submit():
        coll = mongo.db.videos
        data = copy(form.data)
        data['video'] = secure_filename(request.files['video'].filename)
        data['mime_type'] = request.files['video'].content_type
        data['added'] = datetime.utcnow()
        del data['csrf_token']
        inserted = coll.insert_one(data)
        obj = coll.find_one({'_id': inserted.inserted_id},
                            ['_id', 'added', 'thumbs_up', 'thumbs_dn',
                             'name', 'theme', 'video'])
        mongo.save_file(data['video'], request.files['video'], content_type=data['mime_type'])
        return dumps(obj, json_options=RELAXED_JSON_OPTIONS)
    else:
        return form.errors, 400


@app.route('/api/videos/', methods=['GET'])
def api_videos():
    docs = mongo.db.videos.find({}, ['_id', 'added', 'thumbs_up', 'thumbs_dn',
                                     'name', 'theme', 'video', 'mime_type'])
    response = make_response(dumps([doc for doc in docs],
                                   json_options=RELAXED_JSON_OPTIONS), 200)
    response.headers['Content-Type'] = 'application/json'
    return response


@app.route('/api/thumbs/<ObjectId:vid>/', methods=['PUT'])
def api_thumbs(vid):
    data = request.json
    ur = mongo.db.videos.find_one_and_update({'_id': vid},
                                             {'$inc': {'thumbs_%s' % data['dir']: 1}})
    return dumps(ur, json_options=RELAXED_JSON_OPTIONS), 200


@app.route('/download/<path:filename>/', methods=['GET'])
def download(filename):
    video = mongo.send_file(filename)
    response = make_response(video, 200)
    response.headers['Content-type'] = 'video/mpeg'
    return response
