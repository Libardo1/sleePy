sleePy
======

Very rudimentary script to see if I can automate sleep detection with my fitbit.

For a user, makes calls to the fitbit API, and records the last sync time and the number of steps walked. Right now this is recorded in a cvs file. The steps data from the API is a cumulative amount for number of steps walked in a day, so I use the difference since last recorded sync to determine activity If a person is not sleeping but hasn't walked for a period of time (set at 2 hours right now), then the script will still record it as sleeping. Also, if a long time passes between syncs, then the script will probably fail.

The following logic determines when a person slept:
- If time since last sync is less than some fixed time T1
- Then find the last time the person was sleeping
- Starting from that time point, compare the number of steps walked in each success period
- If the change in steps is zero for more than some fixed time T2, then the person is considered asleep

Any new sleeping periods detected are logged with fitbit.

- requires python-fitbit
https://github.com/orcasgit/python-fitbit