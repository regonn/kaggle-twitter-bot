import pandas as pd
import matplotlib.pyplot as plt
from kaggle.api.kaggle_api_extended import KaggleApi
from datetime import datetime as dt
from pytz import timezone

api = KaggleApi()
api.authenticate()

now = dt.now()
now = now.astimezone(timezone('UTC'))
competitions = pd.DataFrame([], columns=['Title', 'ToGo'])
competitions_list = api.competitions_list()
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
