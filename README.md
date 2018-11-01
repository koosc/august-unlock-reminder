# august-unlock-reminder
Trigger HTTP POST to configured when august is left unlocked.


## Configuring
#### ALERT_ENDPOINT
Set where to trigger post when door is unlocked for specified time.

#### ALERT_THRESHOLD
Time in seconds door can be unlocked before triggering alert.

#### AUGUST_TOKEN
Token to authenticate with august. Can be created using ./generate_token.py.

#### AUTO_LOCK
If set door will automatically lock if left unlocked for given amount of time.

### #AUTO_LOCK_THRESHOLD
Time in seconds door can be unlocked before autolocking.

## TODO
- Currently only works for an account with 1 lock and 1 house. (Uses first lock in first house)