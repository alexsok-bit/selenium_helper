import logging
import os.path

import selenium.webdriver

import selenium_helper


def main():
    logger = logging.getLogger(__name__)
    profile = selenium.webdriver.FirefoxProfile()
    # отключаем предупреждение при открытии about:config
    profile.set_preference("browser.aboutConfig.showWarning", False)
    # отключаем трекинг navigator.webdriver
    profile.set_preference("dom.webdriver.enabled", False)
    # отключаем уведомления от сайтов
    profile.set_preference("dom.webnotifications.enabled", False)

    driver = selenium.webdriver.Firefox(
        firefox_binary="bin/firefox-84.0.2/firefox-bin", executable_path="bin/geckodriver", firefox_profile=profile)

    try:
        selenium_helper_extention = selenium_helper.SeleniumHelperExtension(driver)
        selenium_helper_extention.install(os.path.abspath("releases/selenium_helper-0.0.4-fx.xpi"))
        proxy = "http://username:password@host:port"
        cookies = [
            selenium_helper.Cookie(name="cookie", value="test", url="https://whoer.net")
        ]
        selenium_helper_extention.begin_options().set_proxy(proxy).set_cookies(cookies).apply_options()

        driver.get("https://whoer.net/")
        input("Enter to exit...")
    except Exception as e:
        logger.exception(f"{type(e).__name__}{getattr(e, 'args', None)}")
    finally:
        driver.quit()


if __name__ == '__main__':
    main()
