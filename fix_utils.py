import quickfix as fix
import quickfix42 as fix42
from datetime import datetime


def parse_local_side(side: str):
    switcher = {
        'B': fix.Side_BUY,
        'S': fix.Side_SELL
    }
    return switcher.get(side, None)


def parse_fix_side(side):
    switcher = {
        fix.Side_BUY: 'B',
        fix.Side_SELL: 'S'
    }
    return switcher.get(side)


def get_next_ClOrdId():
    return datetime.now().strftime("%Y%m%d-%H%M%S-%f")


class Execution(object):
    clOrdId: str
    symbol: str
    side: str
    price: float
    qty: float


def parse_execution(message: fix.Message) -> Execution:
    execution = Execution()
    execution.clOrdId = message.getField(fix.ClOrdID().getField())
    execution.symbol = message.getField(fix.Symbol().getField())
    execution.side = parse_fix_side(message.getField(fix.Side().getField()))
    execution.price = message.getField(fix.LastPx())
    execution.qty = message.getField(fix.LastShares().getField())

    return execution
