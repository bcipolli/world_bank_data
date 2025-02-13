# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.3'
#       jupytext_version: 1.0.5
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# In this notebook we use the new Sunburst plot by [plotly](http://plot.ly/) to illustrate how the World population
# is splitted among regions and countries. The data set illustrated here originates from the
# [World Bank](https://data.worldbank.org). This notebook is also a quick demo for the 
# [world_bank_data](https://github.com/mwouts/world_bank_data/blob/master/README.md) Python package.

# +
import pandas as pd
import mock
import plotly.offline as offline
import world_bank_data as wb

try:
    # Python 3.6
    from urllib.request import urlopen
except ImportError:
    # Python 2.7
    from urllib import urlopen

# Only show head and tail of dataframes
pd.set_option('display.max_rows', 6)


# Plotly.js in version 1.46.1
def get_latest_plotlyjs(url='https://cdn.plot.ly/plotly-1.46.1.min.js'):
    return urlopen(url).read().decode('utf-8')


with mock.patch('plotly.offline.offline.get_plotlyjs', get_latest_plotlyjs):
    offline.init_notebook_mode()
# -

# Countries and associated regions
countries = wb.get_countries()
countries

# Population dataset, by the World Bank (most recent value)
population = wb.get_series('SP.POP.TOTL', mrv=1)
population

# Same data set, indexed with the country code
population = wb.get_series('SP.POP.TOTL', id_or_value='id', simplify_index=True, mrv=1)
population

# Aggregate region, country and population
df = countries[['region', 'name']].rename(columns={'name': 'country'}).loc[countries.region != 'Aggregates']
df['population'] = population
df

# +
# The sunburst plot requires weights (values), labels, and parent (region, or World)
# We build the corresponding table here
columns = ['parents', 'labels', 'values']

level1 = df.copy()
level1.columns = columns
level1['text'] = level1['values'].apply(lambda pop: '{:,.0f}'.format(pop))

level2 = df.groupby('region').population.sum().reset_index()[['region', 'region', 'population']]
level2.columns = columns
level2['parents'] = 'World'
# move value to text for this level
level2['text'] = level2['values'].apply(lambda pop: '{:,.0f}'.format(pop))
level2['values'] = 0

level3 = pd.DataFrame({'parents': [''], 'labels': ['World'],
                       'values': [0.0], 'text': ['{:,.0f}'.format(population.loc['WLD'])]})

all_levels = pd.concat([level1, level2, level3], axis=0).reset_index(drop=True)
all_levels
# -

# And now we can plot the World Population
offline.iplot(dict(
    data=[dict(type='sunburst', hoverinfo='text', **all_levels)],
    layout=dict(title='World Population (World Bank, 2017)<br>Click on a region to zoom',
                width=800, height=800)),
    validate=False)


