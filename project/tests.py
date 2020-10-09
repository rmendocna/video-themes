import sys
import unittest

from project import create_app


class BasicTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super(BasicTests, cls).setUpClass()
        cls.app = create_app(test_config={'MONGODB_NAME': 'testdb'})

    def empty_storage(self):
        db = self.app.mongo.db
        db.videos.delete_many({})
        db.fs.files.delete_many({})
        db.fs.chunks.delete_many({})

    def setUp(self) -> None:
        self.empty_storage()
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

    def upload(self, filename):
        res = self.client.post('/api/upload/',  # url_for('api_upload'),
                               buffered=True,
                               data=dict(name='test video', theme='theme1',
                                         video=open(filename, 'rb')),
                               )
        self.assertEqual(res.status_code, 200)

    def test_api_upload(self) -> None:
        db = self.app.mongo.db
        count = db.videos.estimated_document_count()
        self.upload('fixtures/video1.mp4')
        self.assertEqual(db.videos.estimated_document_count(), count + 1)
        video = db.videos.find_one({})
        self.assertEqual(video['name'], 'test video')

    def test_api_videos_url(self) -> None:
        resp = self.client.get('/api/videos/')
        assert resp.status_code == 200

    def test_video_api(self):
        self.upload('fixtures/video3.mp4')
        resp = self.client.get('/api/videos/')
        data = resp.json
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'test video')
