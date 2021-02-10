function set_cookies(cookies) {
    for (let cookie of cookies) {
        browser.cookies.set(cookie)
    }
}


function set_proxy(PROXY) {
    // PROXY = {
    //     "type": "http",
    //     "host": "IP address",
    //     "port": "PORT",
    //     "username": "USER NAME",
    //     "password": "PASSWORD"
    // }
    const TARGET = "<all_urls>";
    const CREDENTIALS = {
        username: PROXY.username,
        password: PROXY.password
    }
    const pendingRequests = [];

    function handleProxyRequest(requestInfo) {
        return {type: PROXY.type, host: PROXY.host, port: PROXY.port};
    }

    // A request has completed.
    // We can stop worrying about it.
    function completed(requestDetails) {
        var index = pendingRequests.indexOf(requestDetails.requestId);
        if (index > -1) {
            pendingRequests.splice(index, 1);
        }
    }

    function provideCredentialsSync(requestDetails) {
        // If we have seen this request before, then
        // assume our credentials were bad, and give up.
        if (pendingRequests.indexOf(requestDetails.requestId) != -1) {
            console.log(`bad credentials for: ${requestDetails.requestId}`);
            return {cancel: true};
        }
        pendingRequests.push(requestDetails.requestId);
        console.log(`providing credentials for: ${requestDetails.requestId}`);
        return {authCredentials: CREDENTIALS};
    }

    browser.proxy.onRequest.addListener(
        handleProxyRequest,
        {urls: [TARGET]}
    );

    browser.webRequest.onAuthRequired.addListener(
        provideCredentialsSync,
        {urls: [TARGET]},
        ["blocking"]
    );

    browser.webRequest.onCompleted.addListener(
        completed,
        {urls: [TARGET]}
    );

    browser.webRequest.onErrorOccurred.addListener(
        completed,
        {urls: [TARGET]}
    );
}


function set_headers(HEADERS) {

    function rewriteRequestHeader(requestDetails) {

        for (let key in HEADERS) {
            to_modify = {"name": key, "value": HEADERS[key]};

            is_set = false;

            for (let header of requestDetails.requestHeaders) {
              if (header.name.toLowerCase() === to_modify.name.toLowerCase()) {
                header.value = to_modify.value;
                is_set = true;
              }
            }

            if (!is_set) {
                requestDetails.requestHeaders.push(to_modify)
            }
        }

        return {requestHeaders: requestDetails.requestHeaders}
    }

    const TARGET = "<all_urls>";
    chrome.webRequest.onBeforeSendHeaders.addListener(rewriteRequestHeader,
      { urls: [TARGET] },
      ["blocking", "requestHeaders"]);
}


function main() {

    function setProxy(result) {
        if (result.proxy) {
            console.log("Setup proxy...");
            set_proxy(result.proxy);
        }
    }

    function setCookies(result) {
        if (result.cookies) {
            console.log("Setup cookies...");
            set_cookies(result.cookies);
        }
    }

    function setHeaders(result) {
        if (result.headers) {
            console.log("Setup headers...");
            set_headers(result.headers);
        }
    }

    function onError(error) {
        console.log(`Error: ${error}`);
    }

    let headers = browser.storage.sync.get("headers");
    headers.then(setHeaders, onError);

    let proxy = browser.storage.sync.get("proxy");
    proxy.then(setProxy, onError);

    let cookies = browser.storage.sync.get("cookies");
    cookies.then(setCookies, onError);
}


browser.runtime.onMessage.addListener(function(message, sender, reply) {
    if (message.update) {
        main();
    }
});
