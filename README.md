https://addons.mozilla.org/ru/firefox/addon/selenium-helper/

Дополнение дает возможность установить в браузер прокси с авторизацией по логину и паролю, куки без предварительного открытия страницы для которой эти куки предназначены и заголовки браузера такие как User-Agent и/или Referer.

Пример в директории example.

Суть проблемы с прокси заключается в том, что Firefox поддерживает прокси с авторизацией, но для их использования требуется заполнять alert, а selenium не поддерживает подобные алерты. Для установки кук предварительно требуется открыть сайт для которого эти куки и будут установлены. А заголовки нельзя настроить.

Как это решается с помощью дополнения?

Запускаем браузер

```
import selenium.webdriver

driver = selenium.webdriver.Firefox()
```

Для начала требуется установить дополнение

```
addon_uuid = driver.install_addon("releases/selenium_helper-0.0.6-fx.xpi")
```

Переменная `addon_uuid` будет содержать UUID дополнения указанный в manifest.json самого дополнения, однако после установки у дополнения будет еще один UUID, это внутренний UUID дополнения, зная который возможно открыть страницу настроек дополнения.

Все установленные плагины можно найти на странице `about:config`, чтобы попасть в нее требуется пройти страницу подтверждения. Однако ее можно отключить если до запуска браузера настроить профиль.

```
profile = selenium.webdriver.FirefoxProfile()
# отключаем предупреждение при открытии about:config
profile.set_preference("browser.aboutConfig.showWarning", False)
# отключаем трекинг navigator.webdriver
profile.set_preference("dom.webdriver.enabled", False)
# отключаем уведомления от сайтов
profile.set_preference("dom.webnotifications.enabled", False)

driver = selenium.webdriver.Firefox(firefox_profile=profile)
```

Получаем внутренний UUID дополнения

```
import json

from selenium.webdriver.common.keys import Keys

driver.get("about:config")
search_box = driver.find_element_by_id("about-config-search")
search_box.clear()
search_box.send_keys("extensions.webextensions.uuids")
search_box.send_keys(Keys.ENTER)
search_result = driver.find_elements_by_xpath("//table[@id='prefs']/tr/td/span")
addon_internal_uuid = json.loads(search_result[0].text)[addon_uuid]
```

Теперь, зная внутренний UUID дополнения можно открыть страницу настройки дополнения

```
driver.get(f"moz-extension://{addon_internal_uuid}/data/options.html")
```

А теперь просто вызовем скрипт и передадим нужные нам параметры

```
proxy = urllib.parse.urlparse("http://username:password@host:port")
proxy = {
    "type": proxy.scheme,
    "host": proxy.hostname,
    "port": proxy.port,
    "username": proxy.username,
    "password": proxy.password
}

cookies = [
    {
        "name": "test",
        "value": "any_value",
        "url": "http://same_origin"
    }
]

headers = {
    "User-Agent": "Mozilla User Agent Header"
}

js = f"saveOptionsEx({json.dumps(proxy)}, {json.dumps(cookies)}, {json.dumps(headers)});"
driver.execute_script(js)
```

Куки имеют условие: каждая кука должна содержать параметр `url`, так браузер поймет для какого сайта она предназначена.
