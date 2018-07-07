from dyndns.webapp import app
from unittest import mock
import _helper
import os
import unittest
from bs4 import BeautifulSoup


class Integration(unittest.TestCase):

    def setUp(self):
        os.environ['dyndns_CONFIG_FILE'] = _helper.config_file
        app.config['TESTING'] = True
        self.app = app.test_client()

    def get(self, path, side_effect=None):
        with mock.patch('dns.query.tcp') as tcp:
            with mock.patch('dns.update.Update') as Update:
                with mock.patch('dns.resolver.Resolver') as Resolver:
                    self.mock_tcp = tcp
                    self.mock_Update = Update
                    self.mock_Resolver = Resolver
                    self.mock_resolver = self.mock_Resolver.return_value
                    if side_effect:
                        self.mock_resolver.query.side_effect = side_effect
                    self.response = self.app.get(path)
                    self.data = self.response.data.decode('utf-8')
                    self.mock_update = Update.return_value


class TestMethodUpdateByPath(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    @mock.patch('dyndns.webapp.update_dns_record')
    def test_call_secret_fqdn(self, update):
        update.return_value = 'ok'
        self.app.get('/update-by-path/secret/fqdn')
        update.assert_called_with(secret='secret', fqdn='fqdn', ip_1=None,
                                  ip_2=None)

    @mock.patch('dyndns.webapp.update_dns_record')
    def test_call_secret_fqdn_ip_1(self, update):
        update.return_value = 'ok'
        self.app.get('/update-by-path/secret/fqdn/ip_1')
        update.assert_called_with(secret='secret', fqdn='fqdn', ip_1='ip_1',
                                  ip_2=None)

    @mock.patch('dyndns.webapp.update_dns_record')
    def test_call_secret_fqdn_ip1_ip2(self, update):
        update.return_value = 'ok'
        self.app.get('/update-by-path/secret/fqdn/ip_1/ip_2')
        update.assert_called_with(secret='secret', fqdn='fqdn', ip_1='ip_1',
                                  ip_2='ip_2')


class TestUpdateByPath(Integration):

    @staticmethod
    def _url(path):
        return '/update-by-path/12345678/www.example.com/{}'.format(path)

    def test_ipv4_update(self):
        self.get(self._url('1.2.3.5'),
                 [['1.2.3.4'], ['1.2.3.5']])

        self.mock_update.delete.assert_has_calls([
            mock.call('www.example.com.', 'a'),
            mock.call('www.example.com.', 'aaaa'),
        ])
        self.mock_update.add.assert_called_with('www.example.com.', 300, 'a',
                                                '1.2.3.5')
        self.assertEqual(
            self.data,
            'UPDATED: fqdn: www.example.com. old_ip: 1.2.3.4 new_ip: '
            '1.2.3.5\n',
        )

    def test_ipv6_update(self):
        self.get(self._url('1::3'),
                 [['1::2'], ['1::3']])
        self.mock_update.delete.assert_called_with('www.example.com.', 'aaaa')
        self.mock_update.add.assert_called_with('www.example.com.', 300,
                                                'aaaa', '1::3')
        self.assertEqual(
            self.data,
            'UPDATED: fqdn: www.example.com. old_ip: 1::2 new_ip: 1::3\n',
        )

    def test_ipv4_ipv6_update(self):
        self.get(self._url('1.2.3.5/1::3'),
                 [['1.2.3.4'], ['1.2.3.5'], ['1::2'], ['1::3']])
        self.mock_update.delete.assert_called_with('www.example.com.', 'aaaa')
        self.mock_update.add.assert_called_with('www.example.com.', 300,
                                                'aaaa', '1::3')
        self.assertEqual(
            self.data,
            'UPDATED: fqdn: www.example.com. old_ip: 1.2.3.4 new_ip: 1.2.3.5\n'
            'UPDATED: fqdn: www.example.com. old_ip: 1::2 new_ip: 1::3\n',
        )

    def test_ipv6_ipv4_update(self):
        self.get(self._url('1::3/1.2.3.5'),
                 [['1.2.3.4'], ['1.2.3.5'], ['1::2'], ['1::3']])
        self.mock_update.delete.assert_called_with('www.example.com.', 'aaaa')
        self.mock_update.add.assert_called_with('www.example.com.', 300,
                                                'aaaa', '1::3')
        self.assertEqual(
            self.data,
            'UPDATED: fqdn: www.example.com. old_ip: 1.2.3.4 new_ip: 1.2.3.5\n'
            'UPDATED: fqdn: www.example.com. old_ip: 1::2 new_ip: 1::3\n',
        )


class TestUpdateByQuery(Integration):

    @staticmethod
    def _url(query_string):
        return '/update-by-query?secret=12345678&record_name=www&zone_name=' \
               'example.com&{}'.format(query_string)

    def test_unkown_argument(self):
        self.get('/update-by-query?lol=lol')
        self.assertEqual(
            self.data,
            'PARAMETER_ERROR: Unknown query string argument: "lol"\n',
        )

    def test_ipv4_update(self):
        side_effect = [['1.2.3.4'], ['1.2.3.5']]
        self.get(self._url('ipv4=1.2.3.5'), side_effect)

        self.mock_update.delete.assert_has_calls([
            mock.call('www.example.com.', 'a'),
            mock.call('www.example.com.', 'aaaa'),
        ])
        self.mock_update.add.assert_called_with('www.example.com.', 300, 'a',
                                                '1.2.3.5')
        self.assertEqual(
            self.data,
            'UPDATED: fqdn: www.example.com. old_ip: 1.2.3.4 new_ip: '
            '1.2.3.5\n',
        )

    def test_ipv6_update(self):
        side_effect = [['1::2'], ['1::3']]
        self.get(self._url('ipv6=1::3'), side_effect)
        self.mock_update.delete.assert_called_with('www.example.com.', 'aaaa')
        self.mock_update.add.assert_called_with('www.example.com.', 300,
                                                'aaaa', '1::3')
        self.assertEqual(
            self.data,
            'UPDATED: fqdn: www.example.com. old_ip: 1::2 new_ip: 1::3\n',
        )

    def test_ipv4_ipv6_update(self):
        side_effect = [['1.2.3.4'], ['1.2.3.5'], ['1::2'], ['1::3']]
        self.get(self._url('ipv4=1.2.3.5&ipv6=1::3'), side_effect)
        self.assertEqual(
            self.data,
            'UPDATED: fqdn: www.example.com. old_ip: 1.2.3.4 new_ip: 1.2.3.5\n'
            'UPDATED: fqdn: www.example.com. old_ip: 1::2 new_ip: 1::3\n',
        )

    def test_ip_1_ip_2_update(self):
        side_effect = [['1.2.3.4'], ['1.2.3.5'], ['1::2'], ['1::3']]
        self.get(self._url('ip_1=1.2.3.5&ip_2=1::3'), side_effect)
        self.assertEqual(
            self.data,
            'UPDATED: fqdn: www.example.com. old_ip: 1.2.3.4 new_ip: 1.2.3.5\n'
            'UPDATED: fqdn: www.example.com. old_ip: 1::2 new_ip: 1::3\n',
        )

    def test_invalid_ipv4(self):
        self.get(self._url('ipv4=lol'))
        self.assertEqual(
            self.data,
            'PARAMETER_ERROR: Invalid ip address "lol"\n',
        )

    def test_ttl(self):
        side_effect = [['1.2.3.4'], ['1.2.3.5']]
        self.get(self._url('ipv4=1.2.3.5&ttl=123'), side_effect)
        self.mock_update.add.assert_called_with('www.example.com.', 123, 'a',
                                                '1.2.3.5')


class TestDeleteByPath(Integration):

    @staticmethod
    def _url(fqdn):
        return '/delete-by-path/12345678/{}'.format(fqdn)

    def test_deletion(self):
        self.get(self._url('www.example.com'))

        self.mock_update.delete.assert_has_calls([
            mock.call('www.example.com.', 'a'),
            mock.call('www.example.com.', 'aaaa'),
        ])
        self.mock_update.add.assert_not_called()
        self.assertEqual(
            self.data,
            'UPDATED: Deleted "www.example.com.".\n',
        )


class TestStaticPages(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def get_soup(self, path):
        response = self.app.get(path)
        data = response.data.decode('utf-8')
        return BeautifulSoup(data, 'html.parser')

    def test_index(self):
        response = self.app.get('/')
        data = response.data.decode('utf-8')
        self.assertIn('Usage', data)
        self.assertIn('About', data)
        self.assertIn('https://pypi.org/project/dyndns', data)
        self.assertIn('<!-- dyndns base template -->', data)

    def test_about(self):
        response = self.app.get('/about')
        data = response.data.decode('utf-8')
        self.assertIn('About', data)
        self.assertIn('https://pypi.org/project/dyndns', data)
        self.assertIn('<!-- dyndns base template -->', data)

    def test_docs_installation(self):
        soup = self.get_soup('/docs/installation')
        self.assertEqual(soup.title.string, 'dyndns: Installation')
        response = self.app.get('/docs/installation')
        data = response.data.decode('utf-8')
        self.assertIn('<h1 class="title">Installation</h1>', data)

    def test_docs_configuration(self):
        soup = self.get_soup('/docs/configuration')
        self.assertEqual(soup.title.string, 'dyndns: Configuration')

    def test_docs_usage(self):
        soup = self.get_soup('/docs/usage')
        self.assertEqual(soup.title.string, 'dyndns: Usage')


class TestStatistics(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()
        _helper.remove_updates_db()
        _helper.get_updates_db()

    def get_soup(self, path):
        response = self.app.get(path)
        data = response.data.decode('utf-8')
        return BeautifulSoup(data, 'html.parser')

    def test_statistics(self):
        response = self.app.get('/statistics/updates-by-fqdn')
        data = response.data.decode('utf-8')
        self.assertIn('a.example.com', data)

    def test_latest_submissions(self):
        soup = self.get_soup('/statistics/latest-submissions')
        result = soup.select('tbody tr')
        self.assertEqual(len(result), 12)

        result = soup.select('.is-selected')
        self.assertEqual(len(result), 9)

        result = soup.select('tbody > tr > td:nth-of-type(2)')
        self.assertEqual(result[0].string, 'a.example.com')
        self.assertEqual(result[11].string, 'c.example.com')


if __name__ == '__main__':
    unittest.main()
