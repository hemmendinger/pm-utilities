from selenium import webdriver

def get_page_driver():
    url = 'https://www.gjopen.com/users/sign_in'

    driver = webdriver.Chrome()
    driver.get(url)
    print("Please logon to your Good Judgement account in the browser")
    input("Press enter to continue")

    return driver

