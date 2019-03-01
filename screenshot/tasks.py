import time
import os
from PIL import Image

from intelbot.settings.base import get_secret
from selenium import webdriver

from background_task import background

from celery.schedules import crontab
from celery.task import periodic_task

from celery import task

from intelbot.celery import app
# @task()
# def setup_periodic_tasks(sender, **kwargs):
#     Calls test('world') every 30 seconds
    # sender.add_periodic_task(5.0, make_screenshot, expires=10)

@app.task
def make_screenshot():
    email = get_secret("GOOGLE_ACCOUNT", "EMAIL")
    password = get_secret("GOOGLE_ACCOUNT", "PASSWORD")

    url = 'https://www.google.com/accounts/ServiceLogin?service=ah&passive=true&continue=https://appengine.google.com/_ah/conflogin%3Fcontinue%3Dhttps://www.ingress.com/intel&ltmpl='
    print('start screenshot!')

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("headless")
    chrome_options.add_argument("window-size=1920x1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("disable-gpu")
    print('regist')
    driver = webdriver.Chrome("/home/ubuntu/intelbot/api/chromedriver_64", chrome_options=chrome_options)
    print('get login url')
    driver.get(url)
    print('login')
    driver.find_element_by_name('Email').send_keys(email)
    driver.find_element_by_name('signIn').click()
    driver.find_element_by_name('Passwd').send_keys(password)
    driver.find_element_by_name('signIn').click()


    # kakao image size : 720 x 630 px
    lat = 37.516628
    lag = 127.120052
    zoom_level = 17
    file_name = 'allgong.png'
    file_path = '/home/ubuntu/intelbot/kakao/static/img/'
    filename = file_path + file_name
    url = 'https://www.ingress.com/intel?ll=%f,%f&z=%d' % (lat, lag, zoom_level)
    bounding_box = (600, 150, 1330, 780)

    driver.get(url)
    print('map loading...')
    time.sleep(10)

    driver.save_screenshot(filename)
    print('start crop')
    base_image = Image.open(filename)
    cropped_image = base_image.crop(bounding_box)
    # base_image = base_image.resize(cropped_image.size)
    cropped_image.save(filename)
    # base_image.save(filename)

    # new_screenshot = Screenshot.objects.create(img=screenshot, lat=lat, lag=lag)
    # new_screenshot.save()
    driver.quit()

    # return redirect('/statics/')

@task()
def task_number_two():
    print('task_number_two')
