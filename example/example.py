import logging
import os.path
import os

import selenium.webdriver

import selenium_helper


def main():
    logger = logging.getLogger(__name__)

    if "FIREFOX_PROXY" not in os.environ:
        logger.error("Setup FIREFOX_PROXY in environment and try again!")
        raise SystemExit(1)

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
        selenium_helper_extention.install(os.path.abspath("releases/selenium_helper-0.0.6-fx.xpi"))
        # http://username:password@host:port
        proxy = os.environ["FIREFOX_PROXY"]
        cookies = [
            selenium_helper.Cookie(name="cookie", value="test", url="https://whoer.net")
        ]

        selenium_helper_extention.begin_options().push(proxy, cookies, {})

        driver.get("https://whoer.net/")
        input("Enter to exit...")
    except Exception as e:
        logger.exception(f"{type(e).__name__}{getattr(e, 'args', None)}")
    finally:
        driver.quit()


if __name__ == '__main__':
    main()
