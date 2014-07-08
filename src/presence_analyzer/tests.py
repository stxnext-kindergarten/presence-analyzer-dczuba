# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
import os.path
import json
import datetime
import unittest
from mock import patch
from random import randint

from presence_analyzer import main, views, utils

CURRENT_PATH = os.path.dirname(__file__)
TEST_DATA_CSV = os.path.join(
    CURRENT_PATH, '..', '..', 'runtime', 'data', 'test_data.csv'
)

BAD_TEST_DATA_CSV = os.path.join(
    CURRENT_PATH, '..', '..', 'runtime', 'data', 'bad_test_data.csv'
)

TEST_DATA_XML = os.path.join(
    CURRENT_PATH, '..', '..', 'runtime', 'data', 'test_users.xml'
)

BAD_TEST_DATA_XML = os.path.join(
    CURRENT_PATH, '..', '..', 'runtime', 'data', 'bad_test_users.xml'
)

VALID_HTML_MIME = ('text/html', 'text/html; charset=utf-8')


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
        main.app.config.update({'DATA_XML': TEST_DATA_XML})
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
        self.assertEqual(len(data), 9)
        self.assertDictEqual(
            data[0],
            {u'avatar': u'https://intranet.stxnext.pl:443/api/images/users/36',
             u'name': u'Anna W.', u'user_id': 36}
        )

    def test_presence_start_end_view(self):
        """
        Test user presence start-end view
        """
        url = '/api/v1/presence_start_end/%d'
        user_id = 11
        resp = self.client.get(url % user_id)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 5)
        self.assertEqual(len(data[0]), 3)
        self.assertTrue('Mon' in data[0])

    @patch.object(views.log, 'debug')
    def test_presence_start_end_view_log(self, mock_logger):
        """
        Test user presence start-end view for non-existing user
        """
        url = '/api/v1/presence_start_end/%d'
        user_id = 112312
        resp = self.client.get(url % user_id)
        mock_logger.assert_called_once_with('User %s not found!', user_id)

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

    def test_get_start_end_mean_time(self):
        """
        Test calculating start-end mean time
        """
        users_data = utils.get_data()
        user_mean_time_10 = utils.get_start_end_mean_time(users_data[10])
        user_mean_time_11 = utils.get_start_end_mean_time(users_data[11])

        self.assertEqual(len(user_mean_time_10), 3)
        self.assertEqual(len(user_mean_time_11), 5)

        self.assertIsInstance(user_mean_time_11[0], tuple)
        self.assertIsInstance(user_mean_time_11[4], tuple)
        self.assertIsInstance(user_mean_time_10[2], tuple)

        self.assertIsInstance(user_mean_time_11[2][0], str)
        self.assertIsInstance(user_mean_time_11[3][1], int)
        self.assertIsInstance(user_mean_time_11[1][2], int)

        # time value is in milliseconds
        for row in user_mean_time_10:
            self.assertTrue(0 <= row[1] < 24*60*60*1000,
                            msg="User#10, row data: %s" % str(row))
            self.assertTrue(0 <= row[2] < 24*60*60*1000,
                            msg="User#10, row data: %s" % str(row))

        for row in user_mean_time_11:
            self.assertTrue(0 <= row[1] < 24*60*60*1000,
                            msg="User#11, row data: %s" % str(row))
            self.assertTrue(0 <= row[2] < 24*60*60*1000,
                            msg="User#11, row data: %s" % str(row))

        self.assertEqual(user_mean_time_10[1][0], "Wed")
        self.assertEqual(user_mean_time_10[0][1], 34745000)
        self.assertEqual(user_mean_time_10[1][2], 58057000)
        self.assertEqual(user_mean_time_11[1][1], 33590000)
        self.assertEqual(user_mean_time_11[1][2], 50154000)
        self.assertEqual(user_mean_time_11[3][1], 35602000)
        self.assertEqual(user_mean_time_11[4][2], 54242000)

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

    def test_template_view(self):
        """
        Test template_view view
        """
        resp = self.client.get('/presence_weekday.html')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(resp.content_type, VALID_HTML_MIME)

        resp = self.client.get('mean_time_weekday.html')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(resp.content_type, VALID_HTML_MIME)

        resp = self.client.get('/presence_weekday_asdasd.html')
        self.assertEqual(resp.status_code, 404)
        self.assertIn(resp.content_type, VALID_HTML_MIME)


class PresenceAnalyzerUtilsTestCase(unittest.TestCase):
    """
    Utility functions tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        main.app.config.update({'DATA_XML': TEST_DATA_XML})

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

    def test_group_by_weekday(self):
        """
        Test grouping by weekday
        """
        data = utils.get_data()
        user_10 = utils.group_by_weekday(data[10])

        self.assertEqual(len(user_10), 7)
        self.assertIsInstance(user_10, dict)

        for i in xrange(7):
            self.assertIn(i, user_10, "Iteration with i=%d" % i)
            self.assertIsInstance(user_10[i], list)

        self.assertEqual(user_10[0], [])
        self.assertIsInstance(user_10[1][0], int)

    def test_mean(self):
        """
        Test calculation of mean
        """
        self.assertEqual(utils.mean([]), 0)
        self.assertIsInstance(utils.mean([]), int)
        self.assertIsInstance(utils.mean([1, 2, 3]), float)
        self.assertEqual(utils.mean([1, 2, 3]), 2)
        self.assertEqual(utils.mean([a for a in xrange(-100, 101, -1)]), 0)
        self.assertEqual(utils.mean(
            [123, 234, 345, 456, 567, 678, 789, 890]), 510.25)

        for j in [randint(2, 123) for _ in xrange(randint(2, 123))]:
            self.assertEqual(utils.mean(xrange(1, j)), j/2.0,
                             "Iteration with: a=%s" % j)

    def test_seconds_since_midnight(self):
        """
        Test secounds since midnight calculation
        """
        self.assertEquals(utils.seconds_since_midnight(
            datetime.datetime(1, 1, 1)), 0)
        self.assertIsInstance(utils.seconds_since_midnight(
            datetime.datetime(1, 1, 1)), int)
        self.assertEquals(utils.seconds_since_midnight(
            datetime.datetime(1, 1, 1)), 0)
        self.assertEquals(utils.seconds_since_midnight(
            datetime.time(0, 0, 1)), 1)
        self.assertEquals(utils.seconds_since_midnight(
            datetime.time(12, 0, 0)), 43200)

    def test_interval(self):
        """
        Test interval calculation
        """
        td = datetime.timedelta(hours=4)
        dd1 = datetime.datetime(2013, 5, 1, 12, 05, 04)
        self.assertIsInstance(utils.interval(dd1-td, dd1), int)
        self.assertEqual(utils.interval(dd1-td, dd1), td.seconds)

        dd2 = datetime.datetime(2013, 5, 1, 1, 05, 04)
        self.assertEqual(utils.interval(dd2-td, dd2), td.seconds-24*60*60)

        dn = datetime.datetime.now()
        self.assertEqual(utils.interval(dn, dn), 0)

        dd3 = datetime.time(12, 45, 34)
        dd4 = datetime.time(11, 45, 34)
        self.assertEqual(utils.interval(dd4, dd3), 60*60)

    def test_get_user(self):
        """
        Test for reading data from users.xml
        """
        users = utils.get_users()
        users_items = users.items()

        self.assertEqual(len(users), 9)
        self.assertIsInstance(users, dict)
        self.assertIsInstance(users[122], dict)

        self.assertIn(36, users)
        self.assertIn(122, users)

        self.assertIsInstance(users[122], dict)
        self.assertEqual(len(users_items[1][1]), 2)


class PresenceAnalyzerUtilsWithBadDataTestCase(unittest.TestCase):
    """
    Utility functions tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': BAD_TEST_DATA_CSV})
        main.app.config.update({'DATA_XML': BAD_TEST_DATA_XML})

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

    def test_get_user(self):
        """
        Test for reading data from users.xml with bad entries
        """
        with self.assertRaises(AttributeError):
            utils.get_users()


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
