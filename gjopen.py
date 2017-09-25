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


def carry_forward_forecasts(forecasts: list, answers, start_date: datetime.date, end_date: datetime.date):
    """
    Adds a field denoting if a forecast is a user update or carried forward.
    :param forecasts: Must contain only 1 forecast per user for each day
    :param answers:
    :return:
    """

    # No forecasts exist for days that have not happened
    if end_date > datetime.datetime.utcnow().date():
        end_date = datetime.datetime.utcnow().date()

    days = {start_date + datetime.timedelta(n): list() for n in range(int((end_date - start_date).days + 1))}

    date_keys = [start_date + datetime.timedelta(n) for n in range(int((end_date - start_date).days + 1))]

    for fc in forecasts:
        fc_date = datetime.datetime.strptime(fc['timestamp'], '%Y-%m-%dT%H:%M:%SZ').date()

        days[fc_date].append(fc)

    participants = dict()

    for date in date_keys:
        if date in days:
            for fc in days[date]:
                participants[fc['username']] = fc

    return participants


    # this is unordered
    '''for date, daily_fc_list in days.items():
        for fc in daily_fc_list:
            # Effectively adds participants with their initial forecast
            # or updates a participant's last forecast
            participants[fc['username']] = fc'''





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


def save_dicts_as_csv(data_dict, filename):
    with open(filename, 'x') as file:
        dict_writer = csv.DictWriter(file, data_dict[0].keys())
        dict_writer.writeheader()
        dict_writer.writerows(data_dict)
