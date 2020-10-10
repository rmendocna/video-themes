from os import path
import unittest

from flask import url_for

from project import create_app


class BasicTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super(BasicTests, cls).setUpClass()
        cls.app = create_app(test_config={'MONGODB_NAME': 'testdb'})
        cls.path = path.realpath(path.dirname(__file__))

    def empty_storage(self):
        db = self.app.mongo.db
        db.videos.delete_many({})
        db.fs.files.delete_many({})
        db.fs.chunks.delete_many({})

    def setUp(self) -> None:
        self.empty_storage()
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app_context = self.app.test_request_context()
        self.app_context.push()
        self.client = self.app.test_client()

    def upload(self, filename):
        res = self.client.post(url_for('main.api_upload'),
                               buffered=True,
                               data=dict(name='test video', theme='theme1',
                                         video=open(filename, 'rb')),
                               )
        self.assertEqual(res.status_code, 200)

    def test_api_upload(self) -> None:
        db = self.app.mongo.db
        count = db.videos.estimated_document_count()
        self.upload(path.join(self.path, 'fixtures/video1.mp4'))
        self.assertEqual(db.videos.estimated_document_count(), count + 1)
        video = db.videos.find_one({})
        self.assertEqual(video['name'], 'test video')

    def test_api_videos_url(self) -> None:
        resp = self.client.get(url_for('main.api_videos'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual('application/json', resp.content_type)

    def test_themes_url(self) -> None:
        resp = self.client.get(url_for('main.themes'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('text/html', resp.content_type)

    def test_video_api(self):
        self.upload(path.join(self.path, 'fixtures/video3.mp4'))
        resp = self.client.get(url_for('main.api_videos'))
        self.assertEqual('application/json', resp.content_type)
        data = resp.json
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'test video')

    def thumb_do(self, dir):
        self.upload(path.join(self.path, 'fixtures/video2.mp4'))
        db = self.app.mongo.db
        video = db.videos.find_one({})
        video_id = video['_id']
        token = video.get('thumbs_%s' % dir, 0)
        self.assertEqual(token, 0)
        resp = self.client.put(url_for('main.api_thumbs', vid=video_id),
                               json={'dir': dir})
        self.assertEqual(resp.content_type, 'application/json')
        self.assertEqual(resp.status_code, 200)
        video2 = db.videos.find_one({})
        self.assertEqual(video_id, video2['_id'])
        self.assertEqual(video2['thumbs_%s' % dir], token + 1)

    def test_thumbs_up(self):
        self.thumb_do('up')

    def test_thumbs_dn(self):
        self.thumb_do('dn')
