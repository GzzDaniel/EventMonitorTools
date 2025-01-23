from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from getpass import getpass
from time import sleep

def GetBookingsTable(test=False):
    """ Creates a webDriver instance, prompts user log in, and returns the web html text as a string"""
    print('Initiating please wait')
    
    if test == True:
        # use the downloaded html file for testing purposes
        #f = open('C:\\Users\\gzzed\\OneDrive\\Desktop\\emsc.txt', 'r')
        f = open("C:\\Users\\gzzed\\OneDrive\\Desktop\\pymeetings\\monday28bookings.txt", 'r')
        text = f.read()
        f.close()
        return text
    
    # ___________ INITIALIZATIONS _______________
    options = Options()
    options.add_argument("headless")
    
    driver = webdriver.Edge(options=options)

    wait = WebDriverWait(driver, 60)

    driver.get('https://uconn.7pointops.com/login')

    # _________ WEBSCRAPING BEGIN ___________________________
    element = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/div[1]/div/section/div[2]/section/section/div/div[4]/div/div/div/button')))
    element.click()

    # Change window
    original_window = driver.current_window_handle
    for window_handle in driver.window_handles:
            if window_handle != original_window:
                driver.switch_to.window(window_handle)
                break

    # Get Credentials
    user = input("\nNETID: ")
    passw = getpass()

    # Find Credential slots
    username = driver.find_element(By.ID, value = 'username') 
    password = driver.find_element(By.ID, value = 'password') 

    # Insert Credentials
    username.send_keys(user) 
    password.send_keys(passw)

    login = driver.find_element(by = 'xpath', value = '//*[@id="button"]')
    login.click()

    wait.until(EC.title_contains("Duo Security"))
    print("\nSENDING DUO 2FA, PLEASE CONFIRM \n")

    wait.until(EC.element_to_be_clickable((By.ID, 'trust-browser-button'))).click()

    print("CONFIRMED")

    driver.switch_to.window(original_window)

    button = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/div[1]/div/section/div[2]/section/section/div/div/div/div/div[2]/div/div[2]/div/a/div/div[1]/div/div/i')))
    button.click()

    # get html
    print("loading all bookings, please wait")

    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="dailySetupBookings"]')))
    sleep(10)  # wait for all the booking to load
    
    source_code = driver.page_source
    driver.quit()
    
    return source_code

