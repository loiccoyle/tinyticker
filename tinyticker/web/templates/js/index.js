function add_ticker(){
    let tickers = document.getElementsByClassName("ticker");
    let last_ticker = tickers[tickers.length - 1];
    last_ticker.append(last_ticker.cloneNode(true));
    return false
}
