function saveOptions(e) {
    e.preventDefault();
    let cookies = [];
    let headers = [];
    try {
        cookies = JSON.parse(document.getElementById("cookies").value);
    } catch {};
    try {
        headers = JSON.parse(document.getElementById("headers").value);
    } catch {};
    console.log(cookies)
    browser.storage.sync.set({
        proxy: {
            "type": document.getElementById("type").value,
            "host": document.getElementById("host").value,
            "port": document.getElementById("port").value,
            "username": document.getElementById("username").value,
            "password": document.getElementById("password").value
        },
        cookies: cookies,
        headers: headers
    });

    return false;
}


function saveOptionsEx(proxy, cookies, headers) {
    browser.storage.sync.set({
        proxy: proxy,
        cookies: cookies,
        headers: headers
    });
    browser.runtime.sendMessage({"update": true});
}


function restoreOptions() {

    function setCurrentProxy(result) {
        if (result.proxy) {
            document.getElementById("type").value = result.proxy.type;
            document.getElementById("host").value = result.proxy.host;
            document.getElementById("port").value = result.proxy.port;
            document.getElementById("username").value = result.proxy.username;
            document.getElementById("password").value = result.proxy.password;
        }
    }

    function setCurrentCookies(result) {
        if (result.cookies) {
            document.getElementById("cookies").value = JSON.stringify(result.cookies);
        }
    }

    function setCurrentHeaders(result) {
        if (result.headers) {
            document.getElementById("headers").value = JSON.stringify(result.headers);
        }
    }

    function onError(error) {
        console.log(`Error: ${error}`);
    }

    let headers = browser.storage.sync.get("headers");
    headers.then(setCurrentHeaders, onError);

    let proxy = browser.storage.sync.get("proxy");
    proxy.then(setCurrentProxy, onError);

    let cookies = browser.storage.sync.get("cookies");
    cookies.then(setCurrentCookies, onError);
}


function notifyExtension(e) {
    browser.runtime.sendMessage({"update": true});
}


document.addEventListener("DOMContentLoaded", restoreOptions);
document.getElementById("options_form").addEventListener("submit", saveOptions);
window.addEventListener("submit", notifyExtension);
