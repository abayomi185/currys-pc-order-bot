from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
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

driver_wait = 10
refresh_time = config['refresh_time']

def create_driver():
  if config['headless_mode']:
    chromium_options = Options()
    chromium_options.add_argument("--headless")
    driver = webdriver.Chrome(config['driver_file_path'], options=chromium_options)
    return driver
  else:
    driver = webdriver.Chrome(config['driver_file_path'])
    driver.set_window_size(config['browser_width'],config['browser_height'])
    return driver


def send_notif(message):
  webhook = DiscordWebhook(url=webhook_url,
                  content='{} Stock is available for\n{}'.format(myid, message))
  response = webhook.execute()

def send_notif2(message):
  webhook = DiscordWebhook(url=webhook_url,
                  content='{} Item has been purchased\n{}'.format(myid, message))
  response = webhook.execute()

def is_ping_in_cooldown(prev_ping):
  # global last_ping
  if prev_ping == 0: #initial state
    new_ping = datetime.datetime.now()
    return (False, new_ping)
  else:
    diff = datetime.datetime.now() - prev_ping
    diff_minutes = divmod(diff.total_seconds(), 60)[0]
    if diff_minutes > config['ping_cooldown']:
      return (False, prev_ping)
  return (True, prev_ping)

def run_bot_instance(driver_instance, product):

  #Stagger threads for multiple instances
  time.sleep(refresh_time + (random.random()*10))

  #Create new Chromium driver instance
  driver = driver_instance()

  last_ping = 0

  #Destructure product
  item_name = product['name']
  item_qty = 1
  item_url = product['webpage']

  driver.get(item_url)
  WebDriverWait(driver, driver_wait).until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Accept All Cookies")]'))).click()

  stock = False
  count = False
  purchased = False

  while not stock and not purchased:

    checkout_page = False
    basket_checkout = False
    payment_page = False

    if driver.current_url != item_url:
      driver.get(item_url)

    try:
      add_to_basket = WebDriverWait(driver, driver_wait).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="product-actions"]/div[4]/div[1]/button'))).click()
     
      if config['checkout_addon']:
        try:
          close_dialog = WebDriverWait(driver, driver_wait).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[data-component="CloseBtn"]'))).click()
        except:
          pass
      
      #Continue to basket
      WebDriverWait(driver, driver_wait).until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Continue to basket")]'))).click()

      checkout_page = True
      if config['discord']:
        cooldown = is_ping_in_cooldown(prev_ping=last_ping)
        if not cooldown[0]:
          send_notif(item_url)
        last_ping = cooldown[1]

      time.sleep(1)

      basket_count_str = driver.find_element_by_xpath('//*[@id="root"]/div/div[2]/div/div/div/div[1]/div[1]/div[2]/div/div[1]/div[2]/div[2]/div/div[2]/div/div/div/div/div/span').text
      basket_count = int(basket_count_str)

      if basket_count > item_qty:
        WebDriverWait(driver, driver_wait).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[data-element="DropdownWrapper"]'))).click()
        WebDriverWait(driver, driver_wait).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/div[2]/div/div/div/div[1]/div[1]/div[2]/div/div[1]/div[2]/div[2]/div/div[2]/div/div/div/div/ul/li[1]'))).click()

      time.sleep(1)

      if config['disable_purchase']:
        raise ValueError('Purchase disabled, returning to product page for {}'.format(item_name))

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
        send_notif2(item_url)
      time.sleep(120)

    except Exception as e:
      if config['debug'] == 1:
        if checkout_page:
          print(e)
      elif config['debug'] == 2:
        print(e)
      
    if purchased:
      print("End of script for {}".format(item_name))
      exit()
    
    if checkout_page:
      time.sleep(random.random()*refresh_time)
      driver.get(item_url)
    else:
      currentDT = datetime.datetime.now()
      print("Stock is not available for {} | ".format(item_name) + currentDT.strftime("%H:%M:%S"))
      time.sleep(random.random()*refresh_time)
      driver.refresh()

    # pync.notify("Stock available for " + site_link, open=site_link)

if __name__ == "__main__":

  no_of_sites = len(config['product_data'])

  driver = create_driver

  for x in range(no_of_sites):
    t = threading.Thread(target=run_bot_instance, args=[driver, config['product_data'][x]] )
    t.start()

