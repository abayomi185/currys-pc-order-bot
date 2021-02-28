from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import yaml
import random
import time
import os
import sys
import threading
from discord_webhook import DiscordWebhook
import datetime

conf_import = "./conf.yaml"
secrets_import = "./secrets.yaml"

with open(conf_import, "r") as conf_file:
  config = yaml.safe_load(conf_file)

with open(secrets_import, "r") as secrets_file:
  secrets = yaml.safe_load(secrets_file)

myid = secrets['disord_userid']
webhook_url = secrets['webhook_url']

driver = webdriver.Chrome(config['driver_file_path'])

driver.set_window_size(config['browser_width'],config['browser_height'])

driver_wait = 10

refresh_time = config['refresh_time']

def send_notif(message):
  webhook = DiscordWebhook(url=webhook_url,
                  content='{} Stock is available for\n{}'.format(myid, message))
  response = webhook.execute()

def send_notif2(message):
  webhook = DiscordWebhook(url=webhook_url,
                  content='{} Item has been purchased\n{}'.format(myid, message))
  response = webhook.execute()


def run_bot_instance(site_link):

  driver.get(site_link)
  WebDriverWait(driver, driver_wait).until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Accept All Cookies")]'))).click()

  stock = False
  count = False
  purchased = False
  basket_count = 0

  while not stock and not purchased:

    checkout_page = False
    basket_checkout = False
    payment_page = False

    # print(driver.current_url)

    if driver.current_url != site_link:
      driver.get(site_link)

    try:
      add_to_basket = WebDriverWait(driver, driver_wait).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="product-actions"]/div[4]/div[1]/button'))).click()
     
      if config['checkout_addon']:
        try:
          close_dialog = WebDriverWait(driver, driver_wait).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[data-component="CloseBtn"]'))).click()
        except:
          pass
      
      #Continue to basket
      WebDriverWait(driver, driver_wait).until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Continue to basket")]'))).click()
      
      if basket_count > 0:
        #Reset basket
        try:
          WebDriverWait(driver, driver_wait).until(EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "Remove")]//parent::a'))).click()
          basket_count = 0
          raise ValueError('Deliberate exception raised to reset bot to clean state')
        except:
          pass

      checkout_page = True
      basket_count += 1
      if config['discord']:
        send_notif(site_link)

      time.sleep(1)

      #Go to checkout
      WebDriverWait(driver, driver_wait).until(EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "Go to checkout")]//parent::button'))).click()

      postcode = WebDriverWait(driver, driver_wait).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[aria-label="Postcode Checker"]')))
      postcode.clear()
      postcode.send_keys(secrets['postcode'])
      time.sleep(1)

      #search postcode
      WebDriverWait(driver, driver_wait).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="delivery_location"]/button[2]'))).click()
      # WebDriverWait(driver, driver_wait).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[aria-label="Submit Search"]'))).click()
      # time.sleep(2)
      
      #click delivery
      WebDriverWait(driver, driver_wait).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/div[2]/div[2]/div/div/div[2]/div[2]/div[3]/div[2]/div[1]/ul/li[2]'))).click()
      # time.sleep(3)

      #click free
      WebDriverWait(driver, driver_wait).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/div[2]/div[2]/div/div/div[2]/div[2]/div[3]/div[2]/div[2]/div/div[3]/div[1]/button'))).click()

      email = WebDriverWait(driver, driver_wait).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[autocomplete="email"]')))
      email.clear()
      email.send_keys(secrets['email'])

      #continue after email
      WebDriverWait(driver, driver_wait).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/div[2]/div[2]/div/div/div[3]/div[2]/div[2]/div/div/form/button'))).click()
      # time.sleep(4)
      time.sleep(1)

      password = WebDriverWait(driver, driver_wait).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="password"]')))
      password.clear()
      password.send_keys(secrets['password'])

      #Sign in button
      WebDriverWait(driver, driver_wait).until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Sign in")]'))).click()

      #Card button
      WebDriverWait(driver, driver_wait).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/div[2]/div[2]/div/div/div[4]/div[2]/div[2]/div[2]/div[2]/div[1]/button'))).click()

      payment_page = True

      #Card Number
      card_no = WebDriverWait(driver, driver_wait).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[id="cardNumber"]')))
      card_no.clear()
      card_no.send_keys(secrets['cardno'])

      #Card Holder Name
      card_no = WebDriverWait(driver, driver_wait).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[id="cardholderName"]')))
      card_no.clear()
      card_no.send_keys(secrets['holdername'])

      #Card Month
      month = WebDriverWait(driver, driver_wait).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[id="expiryMonth"]')))
      month.clear()
      month.send_keys(secrets['mm'])

      #Card Year
      year = WebDriverWait(driver, driver_wait).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[id="expiryYear"]')))
      year.clear()
      year.send_keys(secrets['yy'])

      #Card Security Code
      cvv = WebDriverWait(driver, driver_wait).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[id="securityCode"]')))
      cvv.clear()
      cvv.send_keys(secrets['cvv'])

      # Pay
      WebDriverWait(driver, driver_wait).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[id="submitButton"]'))).click()
      purchased = True
      if config['discord']:
        send_notif2(site_link)
      time.sleep(120)

    except Exception as e:
      if config['debug'] and checkout_page:
        print(e)
      
    if purchased:
      print("End of script")
      exit()
    
    if checkout_page:
      time.sleep(random.random()*refresh_time)
      driver.get(site_link)
    else:
      currentDT = datetime.datetime.now()
      print("Stock is not available " + currentDT.strftime("%H:%M:%S"))
      time.sleep(random.random()*refresh_time)
      driver.refresh()

    # pync.notify("Stock available for " + site_link, open=site_link)

if __name__ == "__main__":
  site = sys.argv[1]
  run_bot_instance(site_link=site)

