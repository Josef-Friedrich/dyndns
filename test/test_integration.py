from jfddns import app
from unittest import mock
import _helper
import os
import unittest


class Integration(unittest.TestCase):

    def setUp(self):
        os.environ['JFDDNS_CONFIG_FILE'] = _helper.config_file
        app.config['TESTING'] = True
        self.app = app.test_client()

    def get(self, path, side_effect):
        with mock.patch('dns.query.tcp') as tcp:
            with mock.patch('dns.update.Update') as Update:
                with mock.patch('dns.resolver.Resolver') as Resolver:
                    self.mock_tcp = tcp
                    self.mock_Update = Update
                    self.mock_Resolver = Resolver
                    self.mock_resolver = self.mock_Resolver.return_value
                    self.mock_resolver.query.side_effect = side_effect
                    self.response = self.app.get(path)
                    self.data = self.response.data.decode('utf-8')
                    self.mock_update = Update.return_value


class TestMethodUpdateByPath(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    @mock.patch('jfddns.update_dns_record')
    def test_call_secret_fqdn(self, update):
        update.return_value = 'ok'
        self.app.get('/update-by-path/secret/fqdn')
        update.assert_called_with(secret='secret', fqdn='fqdn', ip_1=None,
                                  ip_2=None)

    @mock.patch('jfddns.update_dns_record')
    def test_call_secret_fqdn_ip_1(self, update):
        update.return_value = 'ok'
        self.app.get('/update-by-path/secret/fqdn/ip_1')
        update.assert_called_with(secret='secret', fqdn='fqdn', ip_1='ip_1',
                                  ip_2=None)

    @mock.patch('jfddns.update_dns_record')
    def test_call_secret_fqdn_ip1_ip2(self, update):
        update.return_value = 'ok'
        self.app.get('/update-by-path/secret/fqdn/ip_1/ip_2')
        update.assert_called_with(secret='secret', fqdn='fqdn', ip_1='ip_1',
                                  ip_2='ip_2')


class TestUpdateByPath(Integration):

    def test_ipv4_update(self):
        self.get('/update-by-path/12345678/www.example.com/1.2.3.5',
                 [['1.2.3.4'], ['1.2.3.5']])

        self.mock_update.delete.assert_called_with('www.example.com.', 'a')
        self.mock_update.add.assert_called_with('www.example.com.', 300, 'a',
                                                '1.2.3.5')
        self.assertEqual(
            self.data,
            'UPDATED fqdn: www.example.com. old_ip: 1.2.3.4 new_ip: 1.2.3.5',
        )

    def test_ipv6_update(self):
        self.get('/update-by-path/12345678/www.example.com/1::3',
                 [['1::2'], ['1::3']])
        self.mock_update.delete.assert_called_with('www.example.com.', 'aaaa')
        self.mock_update.add.assert_called_with('www.example.com.', 300,
                                                'aaaa', '1::3')
        self.assertEqual(
            self.data,
            'UPDATED fqdn: www.example.com. old_ip: 1::2 new_ip: 1::3',
        )


class TestUpdateByQueryString(unittest.TestCase):

    def setUp(self):
        os.environ['JFDDNS_CONFIG_FILE'] = _helper.config_file
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_unkown_argument(self):
        response = self.app.get('/update-by-query?lol=lol')
        self.assertEqual(
            response.data.decode('utf-8'),
            'Unknown query string argument: "lol"',
        )

    @mock.patch('dns.query.tcp')
    @mock.patch('dns.update.Update')
    @mock.patch('dns.resolver.Resolver')
    def test_ipv4_update(self, Resolver, Update, tcp):
        resolver = Resolver.return_value
        resolver.query.side_effect = [['1.2.3.4'], ['1.2.3.5']]
        url = '/update-by-query?secret=12345678&record_name=www&zone_name=' \
              'example.com&ipv4=1.2.3.5'
        response = self.app.get(url)
        update = Update.return_value
        update.delete.assert_called_with('www.example.com.', 'a')
        update.add.assert_called_with('www.example.com.', 300, 'a', '1.2.3.5')
        self.assertEqual(
            response.data.decode('utf-8'),
            'UPDATED fqdn: www.example.com. old_ip: 1.2.3.4 new_ip: 1.2.3.5',
        )


class TestStaticPages(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_about(self):
        response = self.app.get('/about')
        self.assertIn('jfddns (version:', response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
