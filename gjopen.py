from selenium import webdriver
from bs4 import BeautifulSoup
import csv
import time
import datetime

SLEEP = 2


def get_page_driver():
    url = 'https://www.gjopen.com/users/sign_in'

    driver = webdriver.Chrome()
    driver.get(url)
    print("Please logon to your Good Judgement account in the browser")
    input("Press enter to continue")

    return driver


def get_question_info(driver):
    element = driver.find_element_by_xpath('//*[@id="question-detail-tabs"]/li[3]/a')
    driver.execute_script("arguments[0].scrollIntoView();", element)
    element.click()
    time.sleep(SLEEP)

    div = driver.find_element_by_id('question_stats')  # container for row of stats
    h2 = div.find_elements_by_tag_name('h2')  # each stat enclosed in an h2 tag

    info = dict()
    info['no of forecasters'] = int(h2[0].text)
    info['forecast count'] = int(h2[1].text)
    info['forecasts last 24 hours'] = int(h2[2].text)
    info['my no of forecasts'] = int(h2[3].text)

    # Get answer choices
    info['answers'] = [x.text for x in driver.find_elements_by_class_name('answer-name')]

    # Get question open and close UTC times
    open = driver.find_element_by_xpath('//*[@id="main-container"]/div[2]/div[1]/div[1]/div[1]/span[2]/small/span')
    open = open.get_attribute('data-localizable-timestamp')
    info['open'] = datetime.datetime.strptime(open, '%Y-%m-%dT%H:%M:%SZ')

    close = driver.find_element_by_xpath('//*[@id="main-container"]/div[2]/div[1]/div[1]/div[1]/span[4]/small/span')
    close = close.get_attribute('data-localizable-timestamp')
    info['close'] = datetime.datetime.strptime(close, '%Y-%m-%dT%H:%M:%SZ')

    return info


def get_all_forecasts(driver):
    """Assumes page is loaded and scrolled to bottom
    Next, want to load all forecasts automatically
    """
    element = driver.find_element_by_class_name('flyover-comments')
    forecasts = element.find_elements_by_class_name('flyover-comment')
    #soup = BeautifulSoup(element.get_attribute('innerHTML'), 'lxml')
    #forecasts = soup.find_all('div', class_='flyover-comment')
    forecasts = [x.get_attribute('innerHTML') for x in forecasts]

    fc_dicts = list()

    for fc in forecasts:
        fc = prediction_to_dict(fc)

        # Remove comment replies, which are presented in same hierarchy as forecasts
        if fc is not None:
            fc_dicts.append(fc)

    return fc_dicts


def get_my_forecasts(driver, question_url):
    """
    https://www.gjopen.com/questions/425-what-will-be-the-end-of-day-spot-price-of-an-ounce-of-gold-on-29-september-2017
    <a data-remote="true" href="/memberships/14847/forecast_history?page=3&amp;question_id=425">Last »</a>
    :param question_url:
    :return:
    """
    driver.get(question_url)

    # Click on "My Forecasts"
    element = driver.find_element_by_xpath('//*[@id="question-detail-tabs"]/li[4]/a')
    driver.execute_script("arguments[0].scrollIntoView();", element)
    element.click()
    time.sleep(SLEEP)

    # Count how many pages of predictions
    # TODO Ensure works on single page of predicitons
    pagination = driver.find_element_by_class_name('pagination')
    a_tags = pagination.find_elements_by_tag_name('a')

    pred_html = list()

    # get my predictions as Selennium objects
    for n in range(0, len(a_tags) - 2):
        element = driver.find_element_by_id('question_my_forecasts')

        predictions = element.find_elements_by_class_name('flyover-comment')

        pred = [x.get_attribute('innerHTML') for x in predictions]
        pred_html.extend(pred)

        next_link = driver.find_elements_by_link_text('Next ›')

        if next_link:
            driver.execute_script("arguments[0].scrollIntoView();", next_link[0])
            next_link[0].click()

            time.sleep(SLEEP)

    # TODO remove pun
    pred_dicts = list()

    for p in pred_html:
        fc = prediction_to_dict(p)

        # Remove comment replies, which are presented in same hierarchy as forecasts
        if fc is not None:
            pred_dicts.append(fc)

    return pred_dicts


def filter_forecasts(forecasts: list):
    """Remove extraneous forecasts, use UTC as the cutoff
    """

    date0 = datetime.datetime.strptime(forecasts[0]['timestamp'], '%Y-%m-%dT%H:%M:%SZ')

    date1 = datetime.datetime.strptime(forecasts[1]['timestamp'], '%Y-%m-%dT%H:%M:%SZ')

    if date0 > date1:  # Forecasts in descending order (newest to oldest)
        forecasts = reversed(forecasts)

    # Put users' forecasts in bins
    users = dict()
    for fc in forecasts:
        if fc['username'] not in users:
            users[fc['username']] = [fc]
        else:
            users[fc['username']].append(fc)

    filtered_forecasts = []
    for user_bin in users.values():
        filtered_forecasts.extend(filter_last_forecast_per_day(user_bin))

    return filtered_forecasts


def filter_last_forecast_per_day(forecasts: list):
    if len(forecasts) == 1:
        return forecasts

    idx = 0
    next_idx = 1
    loop = True
    saved_forecasts = list()
    while loop:
        date = datetime.datetime.strptime(forecasts[idx]['timestamp'], '%Y-%m-%dT%H:%M:%SZ')
        next_date = datetime.datetime.strptime(forecasts[next_idx]['timestamp'], '%Y-%m-%dT%H:%M:%SZ')

        if date.date() < next_date.date():
            saved_forecasts.append(forecasts[idx])

        idx += 1
        next_idx += 1

        if next_idx == len(forecasts):
            saved_forecasts.append(forecasts[next_idx - 1])
            loop = False

    return saved_forecasts


def carry_forward_my_forecasts(forecasts: list, answers):
    """A forecast is carried forward from one day for each additional day that the forecast is not updated.
    Fill in the list with these datapoints, and ensure only the last forecast for each day is used.
    :param forecasts: list of forecast dicts
    :return: list of forecast dicts with filled in data
    """
    pass


def carry_forward_forecasts(forecasts: list, start_date: datetime.date, end_date: datetime.date):
    """
    Adds a field denoting if a forecast is a user update or carried forward.
    :param forecasts: Must contain only 1 forecast per user for each day
    :param answers:
    :return:
    """

    # No forecasts exist for days that have not happened
    if end_date > datetime.datetime.utcnow().date():
        end_date = datetime.datetime.utcnow().date()

    # Generate set of sequential dates for keys
    date_keys = [start_date + datetime.timedelta(n) for n in range(int((end_date - start_date).days + 1))]
    days = {key: list() for key in date_keys}

    # Put forecasts into bins by date using UTC timestamp
    for fc in forecasts:
        fc_date = datetime.datetime.strptime(fc['timestamp'], '%Y-%m-%dT%H:%M:%SZ').date()
        fc_copy = fc.copy()  # Prevent mutating input
        fc_copy['carryforward'] = False
        days[fc_date].append(fc_copy)

    participants = dict()
    processed = list()

    for date in date_keys:
        # Iterate over list of forecasts for specific date
        for fc in days[date]:
            participants[fc['username']] = fc.copy()

        for user,fc in participants.items():
            fc_date = datetime.datetime.strptime(fc['timestamp'], '%Y-%m-%dT%H:%M:%SZ').date()

            # If forecast is from a previous date, need to carry it forward
            if fc_date != date:
                fc['carryforward'] = True
                fc['timestamp'] = datetime.datetime.strftime(date, '%Y-%m-%dT%H:%M:%SZ')
                fc['timestamp-local'] = ''
                fc_copy = fc.copy()
                processed.append(fc_copy)
            else:
                processed.append(fc.copy())

    return processed


def prediction_to_dict(prediction):
    d = dict()
    soup = BeautifulSoup(prediction, 'lxml')

    # Ignore comment replies
    if not soup.find(class_='prediction-set'):
        return None

    d['username'] = soup.find(class_='membership-username').text

    # Handle deleted comment, which deletes votes
    votes = soup.find(class_='vote-count')
    if hasattr(votes, 'text'):
        d['votes'] = votes.text

    timestamp = soup.find(attrs={'data-localizable-timestamp': True})
    d['timestamp'] = timestamp.attrs['data-localizable-timestamp']
    d['timestamp-local'] = timestamp.text

    answers = soup.find_all(class_='row')

    for n in range(1, len(answers)):  # This skips 1st row which is just a heading
        current = answers[n]
        answer = current.find(class_='col-md-10').text.strip()
        percent_assigned = current.find(class_='col-md-2').text.strip()
        d[answer] = percent_assigned

    return d


def save_forecasts_csv(data_dict, filename, key_order=None):

    if key_order:
        order = ['timestamp', 'username',]

        # Allows including timestamp, username in key_order
        for item in key_order:
            if item in order:
                order.remove(item)

        for key in key_order:
            order.append(key)

        unordered_keys = [x for x in data_dict[0].keys()]

        for item in order:
            unordered_keys.remove(item)

        order.extend(unordered_keys)
        key_order = order
    else:
        key_order = data_dict[0].keys()

    with open(filename, 'x') as file:
        dict_writer = csv.DictWriter(file, key_order)
        dict_writer.writeheader()
        dict_writer.writerows(data_dict)
