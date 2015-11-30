import json
import re
from urllib import quote_plus
from urllib2 import urlopen
from bs4 import BeautifulSoup
import time
import csv
import datetime

import plotly.plotly as py
from plotly.graph_objs import *

from credentials import PLOTLY_KEY, PLOTLY_USER, TROVE_KEY


NEWSPAPER_URL_ROOT = 'http://nla.gov.au/nla.news-title'
TROVE_API_URL = 'http://api.trove.nla.gov.au/result?encoding=json&reclevel=full'


STATES = [
    'ACT',
    'New South Wales',
    'Northern Territory',
    'Queensland',
    'South Australia',
    'Tasmania',
    'Victoria',
    'Western Australia',
    'National'
]


def get_titles_for_state(state):
    '''
    Scrapes Trove to get a list of newspaper title ids for the given state.
    '''
    titles = []
    url = 'http://trove.nla.gov.au/ndp/del/titles?state={}'.format(quote_plus(state))
    response = urlopen(url)
    soup = BeautifulSoup(response.read())
    for link in soup.find_all(href=re.compile('/ndp/del/title/\d+')):
        titles.append(re.match(r'/ndp/del/title/(\d+)', link['href']).group(1))
    return titles


def get_state_totals(state, decade):
    '''
    Gets the total articles by year for the given state and decade.
    '''
    titles = get_titles_for_state(state)
    x = []
    y = []
    url = '{url}&zone=newspaper&key={key}&n=0&l-title={titles}'.format(
        url=TROVE_API_URL,
        key=TROVE_KEY,
        titles='&l-title='.join(titles)
    )
    current_url = '{url}&facet=year&l-decade={decade}&q=date:[{decade}0+TO+{end_year}]'.format(
        url=url,
        decade=decade,
        end_year=(decade * 10) + 9
    )
    print current_url
    results = json.load(urlopen(current_url))
    try:
        for facet in reversed(results['response']['zone'][0]['facets']['facet']['term']):
            x.append(int(facet['display']))
            y.append(int(facet['count']))
            print facet['count']
    except TypeError:
        pass
    return x, y


def create_state_totals_graph():
    '''
    Create a line graph on Plotly showing total articles by state and year.
    '''
    py.sign_in(PLOTLY_USER, PLOTLY_KEY)
    series_data = []
    for state in STATES:
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
            name=state,
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
        name=state,
        )
    series_data.append(series)
    data = Data(series_data)
    layout = Layout(
        title='Trove newspaper articles - {}'.format(state),
        xaxis=XAxis(
            title='Year',
        ),
        yaxis=YAxis(
            title='Number of articles',
        ),
        showlegend=False
    )
    fig = Figure(data=data, layout=layout)

    plot_url = py.plot(fig, filename='trove-newspapers-{}-{}'.format(state.lower().replace(' ', '-'), datetime.datetime.now().isoformat()[:10]))

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
        results = json.load(urlopen(current_url))
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
