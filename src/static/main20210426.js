//See: https://davidwalsh.name/javascript-debounce-function
function debounce(func, wait, immediate) {
  let timeout;
  return function () {
    let context = this,
      args = arguments;
    let later = () => {
      timeout = null;
      if (!immediate) func.apply(context, args);
    };
    let callNow = immediate && !timeout;
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
    if (callNow) func.apply(context, args);
  };
}

const searchbox = document.getElementById("searchbox");
let requestInFlight = null;
searchbox.onkeyup = debounce((event) => {
  if (event.keyCode === 13) {
    document.location = `/search?lang=${
      document.IC_LANG
    }&q=${encodeURIComponent(searchbox.value)}`;
  } else if (event.keyCode === 27) {
    searchbox.value = "";
    document.getElementById("results").innerHTML = "";
  } else {
    const q = searchbox.value;
    const url =
      `/api/search?lang=${document.IC_LANG}&keys=0&size=10&q=` +
      encodeURIComponent(q) +
      "*";

    // Unique object used just for race-condition comparison
    let currentRequest = {};
    requestInFlight = currentRequest;
    fetch(url)
      .then((r) => r.json())
      .then((d) => {
        if (requestInFlight !== currentRequest) {
          // Avoid race conditions where a slow request returns
          // after a faster one.
          return;
        }
        let results =
          `<div id="foundmsg">${d.total} found. Press Enter to see the Search results...</div>` +
          d.result
            .map((r) => `<div><a href="/en/${r}">${r}</a></div>`)
            .join("");
        document.getElementById("results").innerHTML = results;
      });
  }
}, 200); // debounce every 100ms
