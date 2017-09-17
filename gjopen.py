from selenium import webdriver
from bs4 import BeautifulSoup

import time


SLEEP = 2

def get_page_driver():
    url = 'https://www.gjopen.com/users/sign_in'

    driver = webdriver.Chrome()
    driver.get(url)
    print("Please logon to your Good Judgement account in the browser")
    input("Press enter to continue")

    return driver


def get_my_forecasts(driver, question_url):
    '''
    https://www.gjopen.com/questions/425-what-will-be-the-end-of-day-spot-price-of-an-ounce-of-gold-on-29-september-2017
    <a data-remote="true" href="/memberships/14847/forecast_history?page=3&amp;question_id=425">Last »</a>
    :param question_url:
    :return:
    '''
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

    cur_page = 0

    pred_html = list()

    # get my predictions as Selennium objects
    for n in range(0, len(a_tags) - 2):

        element = driver.find_element_by_id('question_my_forecasts')
        #predictions.extend(element.find_elements_by_class_name('prediction-set'))
        predictions = element.find_elements_by_class_name('prediction-set')
        pred = [x.get_attribute('innerHTML') for x in predictions]
        pred_html.extend(pred)

        next = driver.find_elements_by_link_text('Next ›')

        if next:
            driver.execute_script("arguments[0].scrollIntoView();", next[0])
            next[0].click()

            time.sleep(SLEEP)

    # TODO remove pun

    pred_dicts = list()
    for p in pred_html:
        pred_dicts.append(prediction_to_dict(p))

    return pred_dicts


def prediction_to_dict(prediction):
    d = dict()
    soup = BeautifulSoup(prediction, 'lxml')

    d['username'] = soup.find(class_='membership-username').text

    answers = soup.find_all(class_='row')

    for n in range(1, len(answers)):  # This skips 1st row which is just a heading
        current = answers[n]
        answer = current.find(class_='col-md-10').text.strip()
        percent_assigned = current.find(class_='col-md-2').text.strip()
        d[answer] = percent_assigned

    return d


