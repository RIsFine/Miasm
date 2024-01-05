from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.support.wait import WebDriverWait


def connection(url):

    options = Options()
    # options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    driver.get(url)

    # refusing cookies
    driver.find_element("xpath", "//button[@class='jow_prod__sc-ba011d79-6 expDro']").click()

    # bouton connection
    connection_button = "//button[@class='jow_prod__sc-d06221bd-14 gbKUaR']"

    # selection intermarché
    intermarche = "//div[@class='jow_prod__sc-a187e7c-0 grXkOd jow_prod__sc-d216edd-2 jdTOOB'][2]"

    # accepter les condtions d'utilisations
    accept_conditions = "//button[@class='jow_prod__sc-2e941d1e-7 jow_prod__sc-2e941d1e-8 gChOlU kJypop']"

    # bouton connection intermarché
    intermarche_connection_button = "//button[@class='jow_prod__sc-fa79f5b3-2 hezbgj jow_prod__sc-7a4b48cb-2 hXUYpM']"

    driver.find_element("xpath", connection_button).click()
    WebDriverWait(driver, 10).until(lambda x: x.find_element("xpath", intermarche))
    driver.find_element("xpath", intermarche).click()
    driver.find_element("xpath", accept_conditions).click()
    driver.find_element("xpath", intermarche_connection_button).click()

    # Wait for the new window to open (adjust the timeout as needed)
    WebDriverWait(driver, 10).until(lambda instance: len(instance.window_handles) > 1)

    # Switch to the new window handle
    new_window_handle = [handle for handle in driver.window_handles if handle != driver.current_window_handle][0]
    jow = driver.current_window_handle
    driver.switch_to.window(new_window_handle)
    WebDriverWait(driver, 10).until(lambda instance: instance.current_url != 'about:blank')

    username = "//input[@id='username_display']"
    password = "//input[@id='password']"
    login = "//input[@id='kc-login']"

    WebDriverWait(driver, 10).until(lambda x: x.find_element("xpath", username))

    username_field = driver.find_element("xpath", username)
    username_field.send_keys("")
    password_field = driver.find_element("xpath", password)
    password_field.send_keys("")

    driver.find_element("xpath", login).click()
    driver.switch_to.window(jow)
    WebDriverWait(driver, 10).until(lambda x: len(x.window_handles) == 1)

    # driver.close()
    # driver.get(random_recipe)
    add_to_menu(driver, random_recipe2)
    add_to_menu(driver, random_recipe)
    add_to_menu(driver, "https://jow.fr/recipes/soupe-pomme-butternut-88fy8qkz954hhii00krb")

    driver.get("https://jow.fr/grocery/menu")


def add_to_menu(driver: webdriver.Firefox, recipe_url: str):
    driver.get(recipe_url)
    add_button = "//button[@class='jow_prod__sc-fa79f5b3-2 dKrja-D jow_prod__sc-fad4366c-2 hsurVL']"
    driver.find_element("xpath", add_button).click()

    add_anyway_button = "//button[@class='jow_prod__sc-111342c9-8 ixsifS']"

    check_for_unavailability(driver, add_anyway_button)

    # Attendre jusqu'à ce que le bouton "retirer du menu" apparaisse
    withdraw_button = "//button[@class='jow_prod__sc-fa79f5b3-2 dKrja-D jow_prod__sc-fad4366c-2 jow_prod__sc-fad4366c-3 hsurVL Oaxam']"
    WebDriverWait(driver, 10).until(lambda x: driver.find_element("xpath", withdraw_button))


def check_for_unavailability(driver, element):

    try:
        # Use an explicit wait for the ingredient availability window
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, element)))

        # If the window is found, handle the case where ingredients are not available
        print("Ingredients unavailability window found!")
        # Add your logic to handle the case where ingredients are not available
        driver.find_element(By.XPATH, element).click()

    except TimeoutException:
        return
        # If the window is not found within the specified time, proceed with normal flow
        # print("Ingredients unavailability window not found. Proceeding with normal flow.")
        # Add your logic for the case where ingredients are available

    except NoSuchElementException:
        return
        # Handle the case where the element is not found at all
        # print("Element not found. Handle this case accordingly.")
        # Add your logic for the case where the element is not found at all

    # Continue with the rest of your script


# Example usage: update_shopping_cart(['https://recipe1.com', 'https://recipe2.com'])

socle_ps5 = "https://www.amazon.fr/Station-refroidissement-console-manettes-emplacements/dp/B0CLV7KC8H/ref=sr_1_6?crid=QGRDS00K9O04&keywords=socle+ps5&qid=1704354706&sprefix=socle+p%2Caps%2C78&sr=8-6"

random_recipe = "https://jow.fr/recipes/sandwich-thon-avocat-et-concombre-8spgeock7p1uf55q0fz2"
random_recipe2 = "https://jow.fr/recipes/crousti-fajitas-8qfz4vk2dpjnjfto19v0?coversCount=3&from=menu"
# add_to_cart(random_recipe)

connection("https://jow.fr")

