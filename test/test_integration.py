from jfddns import app
import unittest


class TestIntegration(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_without_arguments(self):
        response = self.app.get('/')

        self.assertEqual(response.status, '200 OK')
        self.assertEqual(
            response.data.decode('utf-8'),
            'The configuration file /etc/jfddns.yml could not be found.'
        )


if __name__ == '__main__':
    unittest.main()
