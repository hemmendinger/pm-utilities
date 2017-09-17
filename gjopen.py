from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

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

    # Count how many pages of predictions
    # TODO Ensure works on single page of predicitons
    pagination = driver.find_element_by_class_name('pagination')
    a_tags = pagination.find_elements_by_tag_name('a')

    cur_page = 0

    predictions = list()

    # get my predictions as Selennium objects
    for n in range(0, len(a_tags) - 2):

        element = driver.find_element_by_id('question_my_forecasts')
        predictions.extend(element.find_elements_by_class_name('prediction-set'))

        next = driver.find_elements_by_link_text('Next ›')

        if next:
            driver.execute_script("arguments[0].scrollIntoView();", next[0])
            next[0].click()

            time.sleep(SLEEP)

    # TODO remove pun
    pred_dicts = dict()
    for p in predictions:
        

def prediction_to_dict(prediction):



