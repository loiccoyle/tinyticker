function add_ticker() {
  let tickers = document.getElementsByClassName("ticker");
  let last_ticker = tickers[tickers.length - 1];
  let new_ticker = last_ticker.cloneNode(true);
  new_ticker.className += " uk-animation-slide-right";
  new_ticker.addEventListener("animationend", function () {
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
  ticker.addEventListener("animationend", function () {
    ticker.parentNode.removeChild(ticker);
  });
  ticker.className += " uk-animation-slide-top uk-animation-reverse";
}

function hide_prepost(element) {
  // if the symbol type is not a stock then hide the prepost checkbox
  const prepost = element.parentElement.parentElement.querySelector(
    '[name="ticker-prepost"]',
  );
  if (element.value !== "stock") {
    prepost.parentElement.style.display = "none";
  } else {
    prepost.parentElement.style.display = "block";
  }
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

// convert the form to a json object, for the ticker field, create a list out of the duplicate keys
function formToJson(form) {
  const data = new FormData(form);

  let blank_ticker = () => {
    return {
      layout: {},
    };
  };

  let json = { tickers: [blank_ticker()], sequence: {} };
  let last_ticker = json.tickers[json.tickers.length - 1];
  for (let [key, value] of data.entries()) {
    if (value === "") {
      continue;
    }
    if (value === "on" || value === "1") {
      value = true;
    } else if (value === "off" || value === "0") {
      value = false;
    } else if (!isNaN(value)) {
      value = Number(value);
    }

    if (key.startsWith("ticker-")) {
      let ticker_key = key.replace("ticker-", "");
      if (ticker_key in last_ticker) {
        // if the key is a duplicate then we have moved on to the next ticker
        json.tickers.push(blank_ticker());
        last_ticker = json.tickers[json.tickers.length - 1];
      }

      if (ticker_key.startsWith("layout-")) {
        // if it a layout key then add it to the layout object
        last_ticker.layout[ticker_key.replace("layout-", "")] = value;
      } else {
        last_ticker[ticker_key] = value;
      }
    } else if (key.startsWith("sequence-")) {
      // if it is a sequence key then add it to the sequence object
      json.sequence[key.replace("sequence-", "")] = value;
    } else {
      // if it is not a ticker or sequence key then add it to the json object
      json[key] = value;
    }
  }
  return json;
}
