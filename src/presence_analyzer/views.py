# -*- coding: utf-8 -*-
"""
Defines views.
"""

import calendar
from flask import redirect, render_template, url_for
from jinja2.exceptions import TemplateNotFound

from presence_analyzer.main import app
from presence_analyzer.utils import jsonify, get_data, \
    mean, group_by_weekday, get_start_end_mean_time, get_users

import logging

log = logging.getLogger(__name__)  # pylint: disable=C0103


@app.route('/')
def mainpage():
    """
    Redirects to front page.
    """
    return redirect(url_for('template_view', template='presence_weekday'))


@app.route('/<string:template>.html')
def template_view(template):
    """
    Renders template
    """
    try:
        return render_template('%s.html' % template, template=template)
    except TemplateNotFound:
        return render_template('404.html'), 404


@app.route('/api/v1/users', methods=['GET'])
@jsonify
def users_view():
    """
    Users listing for dropdown.
    """
    users = get_users()
    return [{'user_id': i, 'name': row['name'], 'avatar': row['avatar']}
            for i, row in users.items()]


@app.route('/api/v1/mean_time_weekday/<int:user_id>', methods=['GET'])
@jsonify
def mean_time_weekday_view(user_id):
    """
    Returns mean presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return []

    weekdays = group_by_weekday(data[user_id])
    result = [(calendar.day_abbr[weekday], mean(intervals))
              for weekday, intervals in weekdays.items()]

    return result


@app.route('/api/v1/presence_weekday/<int:user_id>', methods=['GET'])
@jsonify
def presence_weekday_view(user_id):
    """
    Returns total presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return []

    weekdays = group_by_weekday(data[user_id])
    result = [(calendar.day_abbr[weekday], sum(intervals))
              for weekday, intervals in weekdays.items()]

    result.insert(0, ('Weekday', 'Presence (s)'))
    return result


@app.route('/api/v1/presence_start_end/<int:user_id>', methods=['GET'])
@jsonify
def presence_start_end_view(user_id):
    """
    Returns start-end presence of given user grouped by weekday.
    """
    data = get_data()

    try:
        result = get_start_end_mean_time(data[user_id])
    except KeyError:
        log.debug('User %s not found!', user_id)
        return []

    return result
