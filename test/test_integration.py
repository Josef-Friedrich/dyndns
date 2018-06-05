from jfddns import app
from unittest import mock
import _helper
import os
import unittest


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
        update.return_value = 'ok'
        self.app.get('/update/secret/fqdn')
        update.assert_called_with(secret='secret', fqdn='fqdn', ip_1=None,
                                  ip_2=None)

    @mock.patch('jfddns.update_dns_record')
    def test_call_secret_fqdn_ip_1(self, update):
        update.return_value = 'ok'
        self.app.get('/update/secret/fqdn/ip_1')
        update.assert_called_with(secret='secret', fqdn='fqdn', ip_1='ip_1',
                                  ip_2=None)

    @mock.patch('jfddns.update_dns_record')
    def test_call_secret_fqdn_ip1_ip2(self, update):
        update.return_value = 'ok'
        self.app.get('/update/secret/fqdn/ip_1/ip_2')
        update.assert_called_with(secret='secret', fqdn='fqdn', ip_1='ip_1',
                                  ip_2='ip_2')


class TestUpdateByPath(unittest.TestCase):

    def setUp(self):
        os.environ['JFDDNS_CONFIG_FILE'] = _helper.config_file
        app.config['TESTING'] = True
        self.app = app.test_client()

    @mock.patch('dns.query.tcp')
    @mock.patch('dns.update.Update')
    @mock.patch('dns.resolver.Resolver')
    def test_ipv4_update(self, Resolver, Update, tcp):
        resolver = Resolver.return_value
        resolver.query.side_effect = [['1.2.3.4'], ['1.2.3.5']]
        response = self.app.get('/update/12345678/www.example.com/1.2.3.5')
        update = Update.return_value
        update.delete.assert_called_with('www.example.com.', 'a')
        update.add.assert_called_with('www.example.com.', 300, 'a', '1.2.3.5')
        self.assertEqual(
            response.data.decode('utf-8'),
            'UPDATED fqdn: www.example.com old_ip: 1.2.3.4 new_ip: 1.2.3.5',
        )

    @mock.patch('dns.query.tcp')
    @mock.patch('dns.update.Update')
    @mock.patch('dns.resolver.Resolver')
    def test_ipv6_update(self, Resolver, Update, tcp):
        resolver = Resolver.return_value
        resolver.query.side_effect = [['1::2'], ['1::3']]
        response = self.app.get('/update/12345678/www.example.com/1::3')
        update = Update.return_value
        update.delete.assert_called_with('www.example.com.', 'aaaa')
        update.add.assert_called_with('www.example.com.', 300, 'aaaa', '1::3')
        self.assertEqual(
            response.data.decode('utf-8'),
            'UPDATED fqdn: www.example.com old_ip: 1::2 new_ip: 1::3',
        )


if __name__ == '__main__':
    unittest.main()
