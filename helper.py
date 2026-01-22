import pandas as pd
import numpy as np

# -------------------------------
# Medal Tally Helpers
# -------------------------------

def country_year_list(df):
    years = df['Year'].unique().tolist()
    years.sort()
    years.insert(0, 'Overall')

    country = df['region'].dropna().unique().tolist()
    country.sort()
    country.insert(0, 'Overall')

    return years, country


def fetch_medal_tally(df, year, country):
    medal_df = df.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'])

    medal_df = medal_df.groupby(['region', 'Year'])[['Gold', 'Silver', 'Bronze']].sum().reset_index()

    if year == 'Overall' and country == 'Overall':
        temp_df = medal_df.groupby('region')[['Gold', 'Silver', 'Bronze']].sum().reset_index()
    elif year != 'Overall' and country == 'Overall':
        temp_df = medal_df[medal_df['Year'] == int(year)]
    elif year == 'Overall' and country != 'Overall':
        temp_df = medal_df[medal_df['region'] == country]
    else:
        temp_df = medal_df[(medal_df['Year'] == int(year)) & (medal_df['region'] == country)]

    temp_df['Total'] = temp_df['Gold'] + temp_df['Silver'] + temp_df['Bronze']
    temp_df = temp_df.sort_values('Total', ascending=False).reset_index(drop=True)

    return temp_df


# -------------------------------
# Overall Analysis Helpers
# -------------------------------

def data_over_time(df, col):
    temp_df = df.drop_duplicates(['Year', col])
    result = (
        temp_df.groupby('Year')
        .size()
        .reset_index(name=col)
        .sort_values('Year')
    )
    result.rename(columns={'Year': 'Edition'}, inplace=True)
    return result


# -------------------------------
# Country-wise Analysis Helpers
# -------------------------------

def yearwise_medal_tally(df, country):
    temp_df = df.dropna(subset=['Medal'])
    temp_df = temp_df[temp_df['region'] == country]
    result = temp_df.groupby('Year')['Medal'].count().reset_index()
    return result


def country_event_heatmap(df, country):
    temp_df = df.dropna(subset=['Medal'])
    temp_df = temp_df[temp_df['region'] == country]
    pt = temp_df.pivot_table(index='Sport', columns='Year', values='Medal', aggfunc='count').fillna(0)
    return pt


def most_successful_countrywise(df, country):
    temp_df = df.dropna(subset=['Medal'])
    temp_df = temp_df[temp_df['region'] == country]
    x = temp_df['Name'].value_counts().reset_index()
    x.columns = ['Athlete', 'Medals']
    return x.head(10)


# -------------------------------
# Athlete-wise Analysis Helpers
# -------------------------------

def most_successful(df, sport):
    temp_df = df.dropna(subset=['Medal'])

    if sport != 'Overall':
        temp_df = temp_df[temp_df['Sport'] == sport]

    x = temp_df['Name'].value_counts().reset_index()
    x.columns = ['Athlete', 'Medals']
    return x.head(15)


def weight_v_height(df, sport):
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])

    if sport != 'Overall':
        athlete_df = athlete_df[athlete_df['Sport'] == sport]

    return athlete_df[['Name', 'Height', 'Weight', 'Medal', 'Sex']]


def men_vs_women(df):
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])

    male = athlete_df[athlete_df['Sex'] == 'M'].groupby('Year').size().reset_index(name='Male')
    female = athlete_df[athlete_df['Sex'] == 'F'].groupby('Year').size().reset_index(name='Female')

    final = male.merge(female, on='Year', how='left').fillna(0)
    return final
