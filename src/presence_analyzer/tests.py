# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
import os.path
import json
import datetime
import unittest
from mock import patch

from presence_analyzer import main, views, utils

CURRENT_PATH = os.path.dirname(__file__)
TEST_DATA_CSV = os.path.join(
    CURRENT_PATH, '..', '..', 'runtime', 'data', 'test_data.csv'
)

BAD_TEST_DATA_CSV = os.path.join(
    CURRENT_PATH, '..', '..', 'runtime', 'data', 'bad_test_data.csv'
)


# pylint: disable=E1103
class PresenceAnalyzerViewsTestCase(unittest.TestCase):
    """
    Views tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        self.client = main.app.test_client()

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_mainpage(self):
        """
        Test main page redirect.
        """
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)
        assert resp.headers['Location'].endswith('/presence_weekday.html')

    def test_api_users(self):
        """
        Test users listing.
        """
        resp = self.client.get('/api/v1/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 2)
        self.assertDictEqual(data[0], {u'user_id': 10, u'name': u'User 10'})

    def test_mean_time_weekday_view(self):
        """
        Test daily mean time for user
        """
        base_url = '/api/v1/mean_time_weekday/%d'

        resp = self.client.get(base_url % 10)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 7)
        self.assertListEqual(data[1], [u'Tue', 30047.0])
        self.assertListEqual(data[6], [u'Sun', 0])

        resp = self.client.get(base_url % 11)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 7)
        self.assertListEqual(data[2], [u'Wed', 25321.0])
        self.assertListEqual(data[6], [u'Sun', 0])

    @patch.object(views.log, 'debug')
    def test_mean_time_weekday_view_log(self, mock_logger):
        """
        Checks if log.debug is called when requesting for non-existing user
        """
        user_id = 31111111111111111
        resp = self.client.get('/api/v1/mean_time_weekday/%d' % user_id)
        mock_logger.assert_called_once_with('User %s not found!', user_id)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(data, [])

    def test_presence_weekday_view(self):
        """
        Test daily user presence
        """
        base_url = '/api/v1/presence_weekday/%d'

        resp = self.client.get(base_url % 10)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 8)
        self.assertListEqual(data[0], [u'Weekday', u'Presence (s)'])
        self.assertListEqual(data[2], [u'Tue', 30047.0])
        self.assertListEqual(data[6], [u'Sat', 0])

        resp = self.client.get(base_url % 11)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 8)
        self.assertListEqual(data[0], [u'Weekday', u'Presence (s)'])
        self.assertListEqual(data[4], [u'Thu', 45968])
        self.assertListEqual(data[6], [u'Sat', 0])

    @patch.object(views.log, 'debug')
    def test_presence_weekday_view_log(self, mock_logger):
        """
        Test daily user presence for non-existing user
        """
        user_id = 31111111111111111
        resp = self.client.get('/api/v1/presence_weekday/%d' % user_id)
        mock_logger.assert_called_once_with('User %s not found!', user_id)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(data, [])


class PresenceAnalyzerUtilsTestCase(unittest.TestCase):
    """
    Utility functions tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_get_data(self):
        """
        Test parsing of CSV file.
        """
        data = utils.get_data()
        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11])
        sample_date = datetime.date(2013, 9, 10)
        self.assertIn(sample_date, data[10])
        self.assertItemsEqual(data[10][sample_date].keys(), ['start', 'end'])
        self.assertEqual(data[10][sample_date]['start'],
                         datetime.time(9, 39, 5))


class PresenceAnalyzerUtilsWithBadDataTestCase(unittest.TestCase):
    """
    Utility functions tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': BAD_TEST_DATA_CSV})

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    @patch.object(utils.log, 'debug')
    def test_get_data(self, mock_logger):
        """
        Test parsing of CSV file with bad entries
        """
        data = utils.get_data()
        msg = 'Problem with line %d: '
        mock_logger.assert_call_with(msg, 3, exc_info=True)
        mock_logger.assert_call_with(msg, 8, exc_info=True)
        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11])
        self.assertEqual(len(data), 2)
        self.assertEqual(len(data[10])+len(data[11]), 9)


def suite():
    """
    Default test suite.
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(PresenceAnalyzerViewsTestCase))
    test_suite.addTest(unittest.makeSuite(PresenceAnalyzerUtilsTestCase))
    test_suite.addTest(unittest.makeSuite(
        PresenceAnalyzerUtilsWithBadDataTestCase))
    return test_suite


if __name__ == '__main__':
    unittest.main()
