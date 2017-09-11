import os.path
import shutil
from io import BytesIO, StringIO
from os import path
from unittest import TestCase

from webdav3.client import Client


class ClientTestCase(TestCase):
    remote_path_file = 'test_dir/test.txt'
    remote_path_dir = 'test_dir'
    local_path_file = 'test.txt'
    local_path_dir = u'res/test_dir'

    def setUp(self):
        options = {
            'webdav_hostname': 'https://webdav.yandex.ru',
            'webdav_login': 'webdavclient.test',
            'webdav_password': 'Qwerty123!'
        }
        self.client = Client(options)
        if path.exists(path=self.local_path_dir):
            shutil.rmtree(path=self.local_path_dir)

    def test_list(self):
        file_list = self.client.list()
        self.assertIsNotNone(file_list, 'List of files should not be None')
        self.assertGreater(file_list.__len__(), 0, 'Expected that amount of files more then 0')

    def test_free(self):
        self.assertGreater(self.client.free(), 0, 'Expected that free space on WebDAV server is more then 0 bytes')

    def test_check(self):
        self.assertTrue(self.client.check(), 'Expected that root directory is exist')

    def test_mkdir(self):
        if self.client.check(remote_path=self.remote_path_dir):
            self.client.clean(remote_path=self.remote_path_dir)
        self.client.mkdir(remote_path=self.remote_path_dir)
        self.assertTrue(self.client.check(remote_path=self.remote_path_dir), 'Expected the directory is created.')

    def test_download_to(self):
        buff = BytesIO()
        self.client.download_to(buff=buff, remote_path=self.remote_path_file)
        self.assertEquals(buff.getvalue(), 'test content for testing of webdav client')

    def test_download(self):
        self._prepare_for_downloading()

        self.client.download(local_path=self.local_path_dir, remote_path=self.remote_path_dir)

        self.assertTrue(path.exists(self.local_path_dir), 'Expected the directory is downloaded.')
        self.assertTrue(path.isdir(self.local_path_dir), 'Expected this is a directory.')
        self.assertTrue(path.exists(self.local_path_dir + os.path.sep + self.local_path_file),
                        'Expected the file is downloaded')
        self.assertTrue(path.isfile(self.local_path_dir + os.path.sep + self.local_path_file),
                        'Expected this is a file')

    def test_download_sync(self):
        self._prepare_for_downloading()
        os.mkdir(self.local_path_dir)

        def callback():
            self.assertTrue(path.exists(self.local_path_dir + os.path.sep + self.local_path_file),
                            'Expected the file is downloaded')
            self.assertTrue(path.isfile(self.local_path_dir + os.path.sep + self.local_path_file),
                            'Expected this is a file')

        self.client.download_sync(local_path=self.local_path_dir + os.path.sep + self.local_path_file,
                                  remote_path=self.remote_path_file, callback=callback)
        self.assertTrue(path.exists(self.local_path_dir + os.path.sep + self.local_path_file),
                        'Expected the file has already been downloaded')

    def test_download_async(self):
        self._prepare_for_downloading()
        os.mkdir(self.local_path_dir)

        def callback():
            self.assertTrue(path.exists(self.local_path_dir + os.path.sep + self.local_path_file),
                            'Expected the file is downloaded')
            self.assertTrue(path.isfile(self.local_path_dir + os.path.sep + self.local_path_file),
                            'Expected this is a file')

        self.client.download_async(local_path=self.local_path_dir + os.path.sep + self.local_path_file,
                                   remote_path=self.remote_path_file, callback=callback)
        self.assertFalse(path.exists(self.local_path_dir + os.path.sep + self.local_path_file),
                         'Expected the file has not been downloaded yet')

    def test_upload_from(self):
        self._prepare_for_uploading()
        buff = StringIO(u'test content for testing of webdav client')
        self.client.upload_from(buff=buff, remote_path=self.remote_path_file)
        self.assertTrue(self.client.check(self.remote_path_file), 'Expected the file is uploaded.')
        self.test_download_to()

    def test_upload(self):
        self._prepare_for_uploading()
        self.client.upload(remote_path=self.remote_path_file, local_path=self.local_path_dir)
        self.assertTrue(self.client.check(self.remote_path_dir), 'Expected the directory is created.')
        self.assertTrue(self.client.check(self.remote_path_file), 'Expected the file is uploaded.')

    def test_upload_file(self):
        self._prepare_for_uploading()
        self.client.upload_file(remote_path=self.remote_path_file, local_path=self.local_path_file)
        self.assertTrue(self.client.check(remote_path=self.remote_path_file), 'Expected the file is uploaded.')

    def test_upload_sync(self):
        self._prepare_for_uploading()

        def callback():
            self.assertTrue(self.client.check(self.remote_path_dir), 'Expected the directory is created.')
            self.assertTrue(self.client.check(self.remote_path_file), 'Expected the file is uploaded.')

        self.client.upload(remote_path=self.remote_path_file, local_path=self.local_path_dir)

    def test_upload_async(self):
        self._prepare_for_uploading()

        def callback():
            self.assertTrue(self.client.check(self.remote_path_dir), 'Expected the directory is created.')
            self.assertTrue(self.client.check(self.remote_path_file), 'Expected the file is uploaded.')

        self.client.upload(remote_path=self.remote_path_file, local_path=self.local_path_dir)

    def _prepare_for_downloading(self):
        if not self.client.check(remote_path=self.remote_path_dir):
            self.client.mkdir(remote_path=self.remote_path_dir)
        if not self.client.check(remote_path=self.remote_path_file):
            self.client.upload_file(remote_path=self.remote_path_file, local_path=self.local_path_file)

    def _prepare_for_uploading(self):
        if self.client.check(remote_path=self.remote_path_file):
            self.client.clean(remote_path=self.remote_path_file)
        if not self.client.check(remote_path=self.remote_path_dir):
            self.client.mkdir(remote_path=self.remote_path_dir)
        if not path.exists(path=self.local_path_dir):
            os.mkdir(self.local_path_dir)
        if not path.exists(path=self.local_path_dir + os.sep + self.local_path_file):
            shutil.copy(src=self.local_path_file, dst=self.local_path_dir + os.sep + self.local_path_file)
