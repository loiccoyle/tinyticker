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
