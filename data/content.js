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

    function onError(error) {
        console.log(`Error: ${error}`);
    }

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
