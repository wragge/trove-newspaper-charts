import json
from urllib2 import urlopen, HTTPError, Request
import time
import csv
import datetime
from utilities import retry

import plotly.plotly as py
from plotly.graph_objs import *

from credentials import PLOTLY_KEY, PLOTLY_USER, TROVE_KEY


NEWSPAPER_URL_ROOT = 'http://nla.gov.au/nla.news-title'
TROVE_API_URL = 'http://api.trove.nla.gov.au/result?encoding=json&reclevel=full'


STATES = {
    'act': 'ACT',
    'nsw': 'New South Wales',
    'nt': 'Northern Territory',
    'qld': 'Queensland',
    'sa': 'South Australia',
    'tas': 'Tasmania',
    'vic': 'Victoria',
    'wa': 'Western Australia',
    'national': 'National'
}


class ServerError(Exception):
    pass


@retry(ServerError, tries=10, delay=1)
def get_url(url):
    ''' Try to retrieve the supplied url.'''
    req = Request(url)
    try:
        response = urlopen(req)
    except HTTPError as e:
        if e.code == 503 or e.code == 504 or e.code == 500:
            raise ServerError("The server didn't respond")
        else:
            raise
    else:
        return response


def get_titles_for_state(state):
    '''
    Gets a list of newspaper title ids for the given state.
    '''
    titles = []
    url = 'http://api.trove.nla.gov.au/newspaper/titles?state={}&encoding=json&key={}'.format(state, TROVE_KEY)
    response = get_url(url)
    results = json.load(response)
    for title in results['response']['records']['newspaper']:
        titles.append(title['id'])
    return titles


def get_state_totals(state, decade):
    '''
    Gets the total articles by year for the given state and decade.
    '''
    titles = get_titles_for_state(state)
    x = []
    y = []
    totals = {}
    # More than about 350 titles in one url causes server errors
    if len(titles) > 300:
        groups = [titles[:300], titles[300:]]
    else:
        groups = [titles]
    for group in groups:
        url = '{url}&zone=newspaper&key={key}&n=0&l-title={titles}'.format(
            url=TROVE_API_URL,
            key=TROVE_KEY,
            titles='&l-title='.join(group)
        )
        current_url = '{url}&facet=year&l-decade={decade}&q=date:[{decade}0+TO+{end_year}]'.format(
            url=url,
            decade=decade,
            end_year=(decade * 10) + 9
        )
        print current_url
        response = get_url(current_url)
        results = json.load(response)
        try:
            for facet in reversed(results['response']['zone'][0]['facets']['facet']['term']):
                try:
                    totals[int(facet['display'])] += int(facet['count'])
                except KeyError:
                    totals[int(facet['display'])] = int(facet['count'])
        except TypeError:
            pass
    for year in sorted(totals):
        x.append(year)
        y.append(totals[year])
        print totals[year]
    return x, y


def create_state_totals_graph():
    '''
    Create a line graph on Plotly showing total articles by state and year.
    '''
    py.sign_in(PLOTLY_USER, PLOTLY_KEY)
    series_data = []
    for state, state_name in STATES.items():
        x = []
        y = []
        for decade in range(180, 202):
            new_x, new_y = get_state_totals(state, decade)
            x.extend(new_x)
            y.extend(new_y)
            time.sleep(1)
        series = Scatter(
            x=x,
            y=y,
            name=state_name,
        )
        series_data.append(series)
    data = Data(series_data)
    layout = Layout(
        title='Trove newspaper articles by state',
        xaxis=XAxis(
            title='Year',
        ),
        yaxis=YAxis(
            title='Number of articles',
        )
    )
    fig = Figure(data=data, layout=layout)
    plot_url = py.plot(fig, filename='trove-by-state-{}'.format(datetime.datetime.now().isoformat()[:10]))
    return plot_url


def create_state_total_graph(state):
    '''
    Create a line graph on Plotly showing total articles by year for a given state.
    '''
    state_name = STATES[state]
    py.sign_in(PLOTLY_USER, PLOTLY_KEY)
    series_data = []
    x = []
    y = []
    for decade in range(180, 202):
        new_x, new_y = get_state_totals(state, decade)
        x.extend(new_x)
        y.extend(new_y)
    series = Scatter(
        x=x,
        y=y,
        name=state_name,
    )
    series_data.append(series)
    data = Data(series_data)
    layout = Layout(
        title='Trove newspaper articles - {}'.format(state_name),
        xaxis=XAxis(
            title='Year',
        ),
        yaxis=YAxis(
            title='Number of articles',
        ),
        showlegend=False
    )
    fig = Figure(data=data, layout=layout)
    plot_url = py.plot(fig, filename='trove-newspapers-{}-{}'.format(state_name.lower().replace(' ', '-'), datetime.datetime.now().isoformat()[:10]))
    return plot_url


def create_totals_graph():
    '''
    Create a line graph on Plotly showing total articles by year.
    '''
    py.sign_in(PLOTLY_USER, PLOTLY_KEY)
    x = []
    y = []
    for decade in range(180, 200):
        url = '{url}&zone=newspaper&key={key}&n=0'.format(
            url=TROVE_API_URL,
            key=TROVE_KEY,
        )
        current_url = '{url}&facet=year&l-decade={decade}&q=date:[{decade}0+TO+{end_year}]'.format(
            url=url,
            decade=decade,
            end_year=(decade * 10) + 9
        )
        print current_url
        response = get_url(current_url)
        results = json.load(response)
        try:
            for facet in reversed(results['response']['zone'][0]['facets']['facet']['term']):
                x.append(int(facet['display']))
                y.append(int(facet['count']))
                print facet['count']
        except TypeError:
            pass
    series = Scatter(
        x=x,
        y=y
    )
    data = Data([series])
    layout = Layout(
        title='Trove newspaper articles by year',
        xaxis=XAxis(
            title='Year',
        ),
        yaxis=YAxis(
            title='Number of articles',
        )
    )
    fig = Figure(data=data, layout=layout)
    plot_url = py.plot(fig, filename='trove-newspapers-total-{}'.format(datetime.datetime.now().isoformat()[:10]))
    return plot_url


def convert_json_to_csv(json_string):
    data = json.loads(json_string)
    with open('data/data.csv', 'wb') as csv_file:
        csv_writer = csv.writer(csv_file)
        for point in data:
            csv_writer.writerow(point)
