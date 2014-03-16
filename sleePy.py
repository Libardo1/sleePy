import fitbit
import os
import datetime
import time
import pandas

# threshold for time since last sync, in seconds
T1 = 43200
# threshold for deciding if person is sleeping, in seconds
T2 = 7200

user_sleep = pandas.read_csv('user_sleep.csv') # load csv file with 4 columns: time, steps, diff, sleep

client_key = 'client_key_here'
client_pass = 'client_pass_here'
fb = fitbit.FitbitOauthClient(client_key, client_pass)

def check_auth(fb):
    request_token = fb.fetch_request_token()
    token_url = fb.authorize_token_url(request_token)
    # use browser to go to token_url and get the PIN
    return fb.fetch_access_token(request_token, 'PIN')

user_key, user_secret = check_auth(fb)

fb_auth = fitbit.Fitbit(client_key, client_pass, user_key=user_key, user_secret=user_secret)

last_sync = fb_auth.get_devices()[0]['lastSyncTime']
last_sync = time.mktime(time.strptime(last_sync,'%Y-%m-%dT%H:%M:%S.000'))
last_record = user_sleep['time'][user_sleep.shape[0] - 1]

sleep_added = []

if last_sync > last_record:
    stats = fb_auth._COLLECTION_RESOURCE('activities')
    steps = stats['summary']['steps']
    ctime = time.time()
    user_sleep = user_sleep.append({'time': ctime, 'steps': steps, 'diff': 0, 'sleep': 0}, ignore_index=True)
    # Only check sleep if time since last sync is less than T2
    if last_sync - last_record < T1:
        user_sleep['diff'] = user_sleep['steps'].diff()
        # find last sleep
        temp = user_sleep[user_sleep['sleep']==1]
        if not temp.shape[0]:
            # no sleep record yet
            last_sleep_row = 0
        else:
            # find row of last sleep
            last_sleep_row = temp.index[-1]
        # find first diff between steps
        last_steps = user_sleep['steps'][last_sleep_row + 1]
        last_time = user_sleep['time'][last_sleep_row + 1]
        sleep_start_time = 0
        isSleep = 0
        for row in user_sleep.itertuples():
            if row[0] > last_sleep_row + 1:
                if row[2] - last_steps != 0:
                    isSleep = 0
                    sleep_start_time = 0
                    last_sleep_row = row[0]
                    last_steps = user_sleep['steps'][last_sleep_row]
                    last_time = user_sleep['time'][last_sleep_row]
                # sleeping
                if not row[2] - last_steps and row[1] - last_time > 7200:
                    if not isSleep:
                        isSleep = 1
                        sleep_start_time = row[1]
                    for r in range(last_sleep_row, row[0] + 1):
                        user_sleep['sleep'][r] = 1
                        last_time = user_sleep['time'][r]
                    checker = 0
                    for i, sleep in enumerate(sleep_added):
                        if sleep[0] == sleep_start_time:
                            checker = 1
                            sleep_added[i][1] = last_time
                    if not checker:
                        sleep_added.append([sleep_start_time, last_time])

if sleep_added:
    for sleep in sleep_added:
        start_time = datetime.datetime.fromtimestamp(sleep[0])
        duration = int((sleep[1] - sleep[0]) * 1000)
        res = fb_auth.log_sleep(start_time, duration)

user_sleep.to_csv('user_sleep.csv', index=False)
