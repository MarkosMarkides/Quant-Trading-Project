from api.oanda_api import OandaApi
import constants.defs as defs
from infrastructure.instrument_collection import instrumentCollection as ic

def get_trade_units(api: OandaApi, pair, prediction, log_message, stop_loss):

    account_details = api.get_account_summary()
    if (account_details is None) or 'balance' not in account_details:
        log_message(f"get_trade_units() Failed to fetch account balance {pair}")
        return None
    
    account_balance = float(account_details['balance'])
    trade_risk = account_balance * (1 / 100)

    log_message(f"Account Balance: {account_balance}, Risk Percentage: 1%, Trade Risk: {trade_risk}, pair: {pair}", pair)

    prices = api.get_prices([pair])
    if prices is None or len(prices) == 0:
        log_message("get_trade_units() Prices is none", pair)
        return None

    price = None
    for p in prices:
        if p.instrument == pair:
            price = p
            break
    
    if price == None:
        log_message("get_trade_units() price is None????", pair)
        return False

    log_message(f"get_trade_units() price {price}", pair)

    conv = price.buy_conv
    loss = price.ask - stop_loss

    if prediction == defs.SELL:
        conv = price.sell_conv
        loss = stop_loss - price

    pipLocation = ic.instruments_dict[pair].pipLocation
    num_pips = loss / pipLocation

    per_pip_loss = trade_risk / num_pips
    units = per_pip_loss / (conv * pipLocation)

    log_message(f"{pipLocation} {num_pips} {per_pip_loss} {units:.1f}", pair)

    return units