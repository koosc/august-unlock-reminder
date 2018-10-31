import os
from twisted.internet import task
from twisted.internet import reactor
import requests
from datetime import datetime
import logging
import august
from august.authenticator import Authenticator, AuthenticationState

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(message)s')

logger.setLevel(logging.DEBUG)

# Get config values
ALERT_THRESHOLD = int(os.environ.get('ALERT_THRESHOLD', 300))
ALERT_ENDPOINT = os.environ['ALERT_ENDPOINT']
TOKEN = os.environ['AUGUST_TOKEN']


AUTO_LOCK = True if 'AUTO_LOCK' in os.environ else False
AUTO_LOCK_THRESHOLD = int(os.environ.get('AUTO_LOCK_THERESHOLD', 7200))

api = august.api.Api(timeout=20)
# authenticator = Authenticator(api, "email", 'login_email', "password",
#                               access_token_cache_file="token-cache")


# Override timestamp function returned for easier calculations
def epoch_to_datetime(epoch):
    return epoch
august.activity.epoch_to_datetime = epoch_to_datetime

def check_door(token):


    # Get house assuming account only has 1 house
    house = api.get_houses(token)[0]

    # Get lock ID assuming only 1 lock
    lock = api.get_locks(token)[0]

    activities = api.get_house_activities(token, house['HouseID'])


    last_activity = activities[0]
    last_time = last_activity.activity_end_time
    last_action = last_activity.action

    current_time = datetime.now().timestamp() * 1000
    lock_status = api.get_lock_status(token, lock.device_id)

    time_diff = (current_time - last_time) / 1000

    # Check if door has been unlocked for too long
    if time_diff > (ALERT_THRESHOLD) and last_action == 'unlock' and str(lock_status) == 'LockStatus.UNLOCKED':
        logger.info('door left unlocked. sending alert')
        try:
            requests.post(ALERT_ENDPOINT)
        except Exception as e:
            logging.exception('exception making post to alert')
        if time_diff > AUTO_LOCK_THRESHOLD:
            logger.info('auto locking door')
    else:
        logger.debug(f'lock status is {lock_status} for {time_diff} seconds')



logger.debug('starting...')
l = task.LoopingCall(check_door, (TOKEN))
l.start(30)

reactor.run()


