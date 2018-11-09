import os
from twisted.internet import task
from twisted.internet import reactor
import requests
from datetime import datetime
import logging
from august.api import Api 
import august

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(message)s')

logger.setLevel(logging.DEBUG)

# Get config values
ALERT_THRESHOLD = int(os.environ.get('ALERT_THRESHOLD', 300))
ALERT_ENDPOINT = os.environ['ALERT_ENDPOINT']
TOKEN = os.environ['AUGUST_TOKEN']
ALERT_COOLDOWN = os.environ.get('ALERT_COOLDOWN', 600) # time to wait before triggering alert again

AUTO_LOCK = True if 'AUTO_LOCK' in os.environ else False
AUTO_LOCK_THRESHOLD = int(os.environ.get('AUTO_LOCK_THERESHOLD', 7200))

api = Api(timeout=20)

# Override timestamp function returned for easier calculations
def epoch_to_datetime(epoch):
    return epoch
august.activity.epoch_to_datetime = epoch_to_datetime

def check_door(token):
    global last_alert_time

    # Get house assuming account only has 1 house
    house = api.get_houses(token)[0]

    # Get lock ID assuming only 1 lock
    lock = api.get_locks(token)[0]
    lock_id = lock.device_id

    activities = api.get_house_activities(token, house['HouseID'])

    last_activity = activities[0]
    last_time = last_activity.activity_end_time / 1000 # convert to seconds
    last_action = last_activity.action

    current_time = datetime.now().timestamp()
    lock_status = api.get_lock_status(token, lock.device_id)

    time_diff = (current_time - last_time)

    # Check if door has been unlocked for too long
    if time_diff > (ALERT_THRESHOLD) and last_action == 'unlock' and str(lock_status) == 'LockStatus.UNLOCKED':
        try:
            if (current_time - last_alert_time) > ALERT_COOLDOWN:
                logger.info(f'door left unlocked for {time_diff} seconds. sending alert')
                response = requests.post(ALERT_ENDPOINT, timeout=10)
                response.raise_for_status()

                last_alert_time = current_time
            else:
                logger.info(f'no alert sent. {current_time - last_alert_time} seconds since last alert')
        except requests.exceptions.RequestException:
            logger.exception('exception posting alert')
            
        if AUTO_LOCK and time_diff > AUTO_LOCK_THRESHOLD:
            logger.warning('auto locking door')
            api.lock(token, lock_id)
    else:
        logger.debug(f'lock status is {lock_status} for {time_diff} seconds')

if __name__ == '__main__':

    # start last alert to 0 so first will trigger
    last_alert_time = 0

    logger.debug('starting...')
    l = task.LoopingCall(check_door, (TOKEN))

    l.start(30)

    reactor.run()
