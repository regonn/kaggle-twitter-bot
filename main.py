import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv
from kaggle.api.kaggle_api_extended import KaggleApi
from datetime import datetime as dt
from pytz import timezone
import tweepy
import os
import japanize_matplotlib

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
competitions = pd.DataFrame([], columns=['Title', 'enabledDate', 'deadline'])
competitions_list = kaggle_api.competitions_list()
for competition in competitions_list:
    if getattr(competition, 'awardsPoints') and not getattr(competition, 'submissionsDisabled'):
        deadline = getattr(competition, 'deadline')
        deadline = deadline.astimezone(timezone('UTC'))
        diff = deadline - now
        if diff.days > 0:
            competitions = competitions.append(pd.Series([
                getattr(competition, 'title'),
                getattr(competition, 'enabledDate'),
                getattr(competition, 'deadline')], index=['Title', 'enabledDate', 'deadline']),
                ignore_index=True)

plt.figure(figsize=(12, 6))

sns.set(style='white', font="IPAexGothic")
plt.rcParams["font.size"] = 18

compe_name_list = []
for i in range(len(competitions)):
    compe_length = (competitions.iloc[i, 2] - competitions.iloc[i, 1]).days
    compe_to = (competitions.iloc[i, 2] - dt.today()).days
    percent = 1 - compe_to / compe_length
    plt.plot((0, percent), (i, i), linewidth=8.0, c=[0.3, 0.3, 0.3])
    plt.text(1.02, i+0.15, f'{compe_to} days to go')
    plt.plot((percent, 1), (i, i), linewidth=8.0,
             c=[1, 0, 0], alpha=percent*0.9)
    plt.text(0, i+0.2, competitions.iloc[i, 0])
plt.yticks([])
plt.xticks([])
plt.text(1.02, len(competitions) + 0.4, '#かぐるーど')
plt.title('Kaggle Competitions', fontsize='25')

plt.suptitle(dt.strftime(now, '%Y-%m-%d %H:%M:%S %Z'), fontsize='14', y=0.97)
plt.ylim(-0.5, len(competitions) + 0.2)
plt.xlim(-0.04, 1.22)
plt.subplots_adjust(left=0.02, right=0.98, bottom=0.03, top=0.88)
plt.savefig('competitions.png')

twitter_api.update_with_media(
    'competitions.png', "Let's get started Kaggle!! #kaggle #かぐるーど")
