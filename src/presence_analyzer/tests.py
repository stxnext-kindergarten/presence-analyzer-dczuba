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


TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.csv'
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


def suite():
    """
    Default test suite.
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PresenceAnalyzerViewsTestCase))
    suite.addTest(unittest.makeSuite(PresenceAnalyzerUtilsTestCase))
    return suite


if __name__ == '__main__':
    unittest.main()
