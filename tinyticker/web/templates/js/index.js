function add_ticker() {
  let tickers = document.getElementsByClassName("ticker");
  let last_ticker = tickers[tickers.length - 1];
  let new_ticker = last_ticker.cloneNode(true);
  new_ticker.className += " uk-animation-slide-right";
  new_ticker.addEventListener("animationend", function() {
    new_ticker.classList.remove("uk-animation-slide-right");
  });
  last_ticker.insertAdjacentElement("afterend", new_ticker);
}

function remove_ticker(element) {
  let tickers = document.getElementsByClassName("ticker");
  if (tickers.length == 1) {
    return;
  }
  let ticker = element.parentNode.parentNode;
  ticker.addEventListener("animationend", function() {
    ticker.parentNode.removeChild(ticker);
  });
  ticker.className += " uk-animation-slide-top uk-animation-reverse";
}

/**
 * Compares two semver strings.
 *
 * @param {string} v1 - The first version.
 * @param {string} v2 - The second version.
 * @returns {boolean} - Returns true if v1 is greater than v2, otherwise returns false.
 */
function isGreater(v1, v2) {
  let [v1major, v1minor, v1patch] = v1.split(".").map(Number);
  let [v2major, v2minor, v2patch] = v2.split(".").map(Number);
  return (
    v1major > v2major ||
    (v1major == v2major &&
      (v1minor > v2minor || (v1minor == v2minor && v1patch > v2patch)))
  );
}

async function checkForUpdate(currentVersion) {
  const url = "https://pypi.org/pypi/tinyticker/json";
  const response = await fetch(url);
  const data = await response.json();
  const pypiVersion = data.info.version;
  return isGreater(pypiVersion, currentVersion);
}

