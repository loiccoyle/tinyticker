function add_ticker() {
  let tickers = document.getElementsByClassName("ticker");
  let last_ticker = tickers[tickers.length - 1];
  last_ticker.insertAdjacentElement("afterend", last_ticker.cloneNode(true));
}

function remove_ticker(element) {
  let tickers = document.getElementsByClassName("ticker");
  if (tickers.length == 1) {
    return;
  }
  let ticker = element.parentNode;
  ticker.addEventListener("animationend", function () {
    ticker.parentNode.removeChild(ticker);
  });
  ticker.classList.remove("uk-animation-slide-right");
  ticker.className += " uk-animation-slide-top uk-animation-reverse";
}
