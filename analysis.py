from datetime import datetime

def calculate_daily_brier_score(forecasts: list, answer_keys: dict):
    '''

    :param forecasts:
    :param answer_keys: Dictionary with answer keys as keys and True or False as the values
    :return:
    '''

    # timestamp formatted as  '2017-09-03T16:31:49Z'
    prev_dt = datetime.strptime(forecasts[0]['timestamp'], '%Y-%m-%dT%H:%M:%SZ')

    for fc in forecasts:
        # see if date is equal to same day as prev, if
        pass


def score_forecast(forecast: dict, answer_keys: dict):
    '''
    Order is irrelevant.
    :param forecast:
    :param answer_keys:
    :return:
    '''
    # Converts string percent to decimal
    pct = lambda x: int(x.strip('%')) / 100

    score = 0

    for k in answer_keys.keys():
        if answer_keys[k] is False:
            score += (0 - pct(forecast[k]))**2
        else:
            score += (1 - pct(forecast[k]))**2

    return score
