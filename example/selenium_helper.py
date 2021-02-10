#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
#
# Created at 19.01.2021.
# Python 3.7.3 x64
# Contacts: alexandrsokolov@cock.li
#
import copy
import json
import urllib.parse
from functools import lru_cache
from typing import List, Dict

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

OPTION_PROXY_TYPE = "proxy_type"
OPTION_PROXY_HOST = "proxy_host"
OPTION_PROXY_PORT = "proxy_port"
OPTION_PROXY_USERNAME = "proxy_username"
OPTION_PROXY_PASSWORD = "proxy_password"
OPTION_PROXY_COOKIES = "proxy_cookies"
OPTION_HEADERS = "headers"


class NoAddonException(Exception):
    pass


class CookieException(Exception):
    pass


class Cookie(dict):
    """https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/API/cookies/set"""

    def __init__(self, *, domain=None, expiration_date=None, first_party_domain=None, http_only=None, name=None,
                 path=None, same_site=None, secure=None, store_id=None, url=None, value=None):
        super().__init__()
        if domain:
            self.domain = domain
        if expiration_date:
            self.expiration_date = expiration_date
        if first_party_domain:
            self.first_party_domain = first_party_domain
        if http_only:
            self.http_only = http_only
        if name:
            self.name = name
        if path:
            self.path = path
        if same_site:
            self.same_site = same_site
        if secure:
            self.secure = secure
        if store_id:
            self.store_id = store_id
        if url:
            self.url = url
        if value:
            self.value = value

    @property
    def domain(self):
        """A string representing the domain of the cookie. If omitted, the cookie becomes a host-only cookie."""
        return self.get("domain")

    @domain.setter
    def domain(self, value):
        self["domain"] = value

    @domain.deleter
    def domain(self):
        del self["domain"]

    @property
    def expiration_date(self):
        """A number that represents the expiration date of the cookie as the number of seconds since the UNIX epoch.
        If omitted, the cookie becomes a session cookie."""
        return self.get("expirationDate")

    @expiration_date.setter
    def expiration_date(self, value):
        self["expirationDate"] = value

    @expiration_date.deleter
    def expiration_date(self):
        del self["expirationDate"]

    @property
    def first_party_domain(self):
        """A string representing the first-party domain with which the cookie to will be associated.
        This property must be supplied if the browser has first-party isolation enabled. See First-party isolation
        https://developer.mozilla.org/en-US/Add-ons/WebExtensions/API/cookies#First-party_isolation"""
        return self.get("firstPartyDomain")

    @first_party_domain.setter
    def first_party_domain(self, value):
        self["firstPartyDomain"] = value

    @first_party_domain.deleter
    def first_party_domain(self):
        del self["firstPartyDomain"]

    @property
    def http_only(self):
        """A boolean that specifies whether the cookie should be marked as HttpOnly (true), or not (false).
        If omitted, it defaults to false."""
        return self.get("httpOnly")

    @http_only.setter
    def http_only(self, value):
        self["httpOnly"] = value

    @http_only.deleter
    def http_only(self):
        del self["httpOnly"]

    @property
    def name(self):
        """A string representing the name of the cookie. If omitted, this is empty by default."""
        return self.get("name")

    @name.setter
    def name(self, value):
        self["name"] = value

    @name.deleter
    def name(self):
        del self["name"]

    @property
    def path(self):
        """A string representing the path of the cookie.
        If omitted, this defaults to the path portion of the URL parameter."""
        return self.get("path")

    @path.setter
    def path(self, value):
        self["path"] = value

    @path.deleter
    def path(self):
        del self["path"]

    @property
    def same_site(self):
        """A cookies.SameSiteStatus value that indicates the SameSite state of the cookie.
        If omitted, it defaults to 0, 'no_restriction'.
        https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/API/cookies/SameSiteStatus"""
        return self.get("sameSite")

    @same_site.setter
    def same_site(self, value):
        self["sameSite"] = value

    @same_site.deleter
    def same_site(self):
        del self["sameSite"]

    @property
    def secure(self):
        """A boolean that specifies whether the cookie should be marked as secure (true), or not (false).
        If omitted, it defaults to false."""
        return self.get("secure")

    @secure.setter
    def secure(self, value):
        self["secure"] = value

    @secure.deleter
    def secure(self):
        del self["secure"]

    @property
    def store_id(self):
        """A string representing the ID of the cookie store in which to set the cookie.
        If omitted, the cookie is set in the current execution context's cookie store by default."""
        return self.get("storeId")

    @store_id.setter
    def store_id(self, value):
        self["storeId"] = value

    @store_id.deleter
    def store_id(self):
        del self["storeId"]

    @property
    def url(self):
        """A string representing the request-URI to associate with the cookie.
        This value can affect the default domain and path values of the created cookie."""
        return self.get("url")

    @url.setter
    def url(self, value):
        self["url"] = value

    @url.deleter
    def url(self):
        del self["url"]

    @property
    def value(self):
        """A string representing the value of the cookie.
        If omitted, this is empty by default."""
        return self.get("value")

    @value.setter
    def value(self, value):
        self["value"] = value

    @value.deleter
    def value(self):
        del self["value"]


class SeleniumHelperExtension:
    """Обертка для установки и настройки дополнения"""

    _uuid = None

    _options = {
        OPTION_PROXY_TYPE: "type",
        OPTION_PROXY_HOST: "host",
        OPTION_PROXY_PORT: "port",
        OPTION_PROXY_USERNAME: "username",
        OPTION_PROXY_PASSWORD: "password",
        OPTION_PROXY_COOKIES: "cookies",
        OPTION_HEADERS: "headers"
    }

    def __init__(self, driver: Firefox, raise_for_about_config=True):
        self.raise_for_about_config = raise_for_about_config
        self._driver = driver

    @property
    def uuid(self):
        return self._uuid

    @property
    def internal_uuid(self):
        installed_addons = json.loads(self._get_preference("extensions.webextensions.uuids"))
        try:
            return installed_addons[self.uuid]
        except KeyError:
            raise NoAddonException("Addon `selenium_helper` not found. Is it installed?")

    @property
    def setup_url(self):
        return f"moz-extension://{self.internal_uuid}/data/options.html"

    def set_uuid(self, uuid: str):
        """если дополнение уже установлено, требуется его UUID для того чтобы найти дополнение в списке
        установленных и получить его внутренний UUID"""
        self._uuid = uuid

    def install_debug(self):
        """открываем страницу отладки дополнений и предоставляем возможность установить дополнение из файла"""
        self._driver.get("about:debugging#/runtime/this-firefox")
        if self._uuid:
            input("Install extension from file and press Enter to continue...")
        else:
            self._uuid = input("Install extension from file and enter UUID:")

    def install(self, xpi_path: str):
        """установка дополнения в браузер"""
        self._uuid = self._driver.install_addon(xpi_path)

    def begin_options(self):
        """открываем настройки дополнения"""
        self._driver.get(self.setup_url)
        return self

    def set_proxy(self, proxy_string: str):
        """заполняем поля для прокси"""
        proxy = urllib.parse.urlparse(proxy_string)
        self._fill_option(OPTION_PROXY_TYPE, proxy.scheme)
        self._fill_option(OPTION_PROXY_HOST, proxy.hostname)
        self._fill_option(OPTION_PROXY_PORT, proxy.port)
        try:
            self._fill_option(OPTION_PROXY_USERNAME, proxy.username)
            self._fill_option(OPTION_PROXY_PASSWORD, proxy.password)
        except TypeError:
            pass
        return self

    def set_cookies(self, cookies: List[Cookie], default_url=None, ignore_errors=False):
        """устанавливаем куки. у кук должен быть url, если его нет, то попытаемся создать его из полей domain и path,
        если это не получится сделать, то будем использовать переменную default_url, если она не установлена,
        то выбрасываем исключение, а если ignore_errors установлен в True, то пропускаем проблемную куку."""
        clear_value = self._clear_cookies(cookies, default_url, ignore_errors)

        value = json.dumps(clear_value)

        self._fill_option(OPTION_PROXY_COOKIES, value)
        return self

    def set_headers(self, headers: List[Dict[str, str]]):
        """устанавливаем заголовки браузера, для всех запросов."""
        value = json.dumps(headers)
        self._fill_option(OPTION_HEADERS, value)
        return self

    def push(self, proxy, cookies, headers):

        if proxy:
            proxy = urllib.parse.urlparse(proxy)
            proxy = {
                "type": proxy.scheme,
                "host": proxy.hostname,
                "port": proxy.port,
                "username": proxy.username,
                "password": proxy.password
            }

        js = f"""saveOptionsEx({json.dumps(proxy)}, {json.dumps(cookies)}, {json.dumps(headers)});"""
        self._driver.execute_script(js)
        return self

    def apply_options(self):
        """сохраняем изменения сделанные на странице настроек"""
        self._driver.find_element_by_id("submit").click()

    def clear_cookies(self, cookies: List[Cookie], default_url=None, ignore_errors=False):
        return self._clear_cookies(cookies, default_url, ignore_errors)

    def _clear_cookies(self, cookies: List[Cookie], default_url=None, ignore_errors=False):
        clear_value = []

        for cookie in copy.deepcopy(cookies):
            if not cookie.get("url"):
                try:
                    domain = cookie["domain"][1:] if cookie["domain"].startswith(".") else cookie["domain"]
                    url = f"http://{domain}{cookie.get('path', '/')}"
                except KeyError:
                    url = default_url

                if url is None:
                    if ignore_errors:
                        continue
                    else:
                        raise CookieException(f"No url specified for cookie {cookie}")

                cookie["url"] = url
            clear_value.append(cookie)
        return clear_value

    def _fill_option(self, name, value):
        self._fill_element(self._driver.find_element_by_id(self._options[name]), value)

    @lru_cache()
    def _get_preference(self, name):

        def get_search_box_with_wait_about_config_approved():
            try:
                search_box = self._driver.find_element_by_id("about-config-search")  # noqa
            except NoSuchElementException:
                if self.raise_for_about_config:
                    raise
                else:
                    input("Approve warning message and press Enter to continue...")
                    return get_search_box_with_wait_about_config_approved()
            else:
                return search_box

        self._driver.get("about:config")

        search_box = get_search_box_with_wait_about_config_approved()
        search_box.clear()
        search_box.send_keys(name)
        search_box.send_keys(Keys.ENTER)

        search_result = self._driver.find_elements_by_xpath("//table[@id='prefs']/tr/td/span")
        return search_result[0].text

    def _fill_element(self, element, value: str):  # noqa
        element.clear()
        element.send_keys(value)
