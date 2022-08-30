function add_ticker() {
  let tickers = document.getElementsByClassName("ticker");
  let last_ticker = tickers[tickers.length - 1];
  last_ticker.insertAdjacentElement("afterend", last_ticker.cloneNode(true));
}

function remove_ticker(element) {
  let ticker = element.parentNode;
  ticker.parentNode.removeChild(ticker);
}
