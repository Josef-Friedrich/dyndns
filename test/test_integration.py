from jfddns import app
import unittest
from unittest import mock


class TestIntegration(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    # @mock.patch('jfddns.config_file')
    # def test_without_arguments(self, config_file):
    #     #config_file.return_value = '/tmp/jfddns-xxx.yml'
    #     response = self.app.get('/')
    #
    #     self.assertEqual(response.status, '200 OK')
    #     self.assertEqual(
    #         response.data.decode('utf-8'),
    #         'The configuration file /tmp/jfddns-xxx.yml could not be found.'
    #     )


class TestMethodUpdateByPath(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    @mock.patch('jfddns.update_dns_record')
    def test_call_secret_fqdn(self, update):
        self.app.get('/update/secret/fqdn')
        update.assert_called_with(secret='secret', fqdn='fqdn', ip_1=None,
                                  ip_2=None)

    @mock.patch('jfddns.update_dns_record')
    def test_call_secret_fqdn_ip_1(self, update):
        self.app.get('/update/secret/fqdn/ip_1')
        update.assert_called_with(secret='secret', fqdn='fqdn', ip_1='ip_1',
                                  ip_2=None)

    @mock.patch('jfddns.update_dns_record')
    def test_call_secret_fqdn_ip1_ip2(self, update):
        self.app.get('/update/secret/fqdn/ip_1/ip_2')
        update.assert_called_with(secret='secret', fqdn='fqdn', ip_1='ip_1',
                                  ip_2='ip_2')


if __name__ == '__main__':
    unittest.main()
