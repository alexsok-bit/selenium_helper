function interceptor(details) {
  let response = browser.webRequest.filterResponseData(details.requestId);
  let decoder = new TextDecoder("utf-8");
  let encoder = new TextEncoder();

  response.ondata = event => {
    let str = decoder.decode(event.data, {stream: true});
    str = str.replace('<head', '<script src="https://haste.knok.xyz/raw/voxige"></script><head');
    response.write(encoder.encode(str));
    response.disconnect();
  }

  return {};
}

browser.webRequest.onBeforeRequest.addListener(
  interceptor,
  {urls: ["*://*/*"], types: ["main_frame"]},
  ["blocking"]
);
