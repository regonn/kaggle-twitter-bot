import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from kaggle.api.kaggle_api_extended import KaggleApi
from datetime import datetime as dt
from pytz import timezone
import tweepy
import os

if os.environ.get("PRODUCTION") is None:
    load_dotenv(verbose=True)

consumer_key = os.environ.get('TWITTER_CONSUMER_KEY')
consumer_secret = os.environ.get('TWITTER_CONSUMER_SECRET')
access_token = os.environ.get('TWITTER_ACCESS_TOKEN')
access_token_secret = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

twitter_api = tweepy.API(auth)

kaggle_api = KaggleApi()
kaggle_api.authenticate()

now = dt.now()
now = now.astimezone(timezone('UTC'))
competitions = pd.DataFrame([], columns=['Title', 'ToGo'])
competitions_list = kaggle_api.competitions_list()
for competition in competitions_list:
    if getattr(competition, 'awardsPoints') and not getattr(competition, 'submissionsDisabled'):
        deadline = getattr(competition, 'deadline')
        deadline = deadline.astimezone(timezone('UTC'))
        diff = deadline - now
        if diff.days > 0:
            competitions = competitions.append(pd.Series([
                getattr(competition, 'title') +
                '({} days to go)'.format(diff.days + 1),
                diff.days + 1], index=['Title', 'ToGo']), ignore_index=True)

titles = competitions['Title']
togo = competitions['ToGo']

plt.figure(figsize=(12, 6))
plt.barh(range(len(titles)), togo, .3, left=0)
plt.tick_params(axis='both', which='major', labelsize=15)
plt.tick_params(axis='both', which='minor', labelsize=20)
plt.title('Kaggle Competitions', fontsize='25')
plt.suptitle(dt.strftime(now, '%Y-%m-%d %H:%M:%S %Z'))
plt.xlabel('Days', fontsize='20')
plt.yticks(range(len(titles)), "")
plt.axis('off')

for i in range(len(titles)):
    plt.text(0,
             i+.25, titles.iloc[i],
             ha='left', fontsize='12')
plt.savefig('competitions.png')

twitter_api.update_with_media('competitions.png', "Let's get started Kaggle!! #kaggle")
