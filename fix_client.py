import threading
import time
from fix_utils import *
import quickfix as fix
import uuid


class FixClient(fix.Application):
    sessionID = None
    ready = False
    orders = {}
    executions = {}
    executions_lock = threading.Lock()

    def is_ready(self):
        return self.ready

    def __init__(self):
        super().__init__()

    def onCreate(self, session):
        print("Application created - session: " + session.toString())
        self.sessionID = session
        pass

    def onLogon(self, session):
        print("onLogon")
        self.ready = True
        pass

    def onLogout(self, session):
        print("onLogout")
        self.ready = False
        pass

    def fromAdmin(self, message, sessionId):
        print("fromAdmin", message)
        pass

    def fromApp(self, message: fix.Message, sessionId: fix.SessionID):
        print("fromApp", message)
        msgType = message.getHeader().getField(fix.MsgType().getField())
        if msgType == fix.MsgType_Heartbeat:
            self.process_heart_beat(message=message, sessionId=sessionId)
        elif msgType == fix.MsgType_ExecutionReport:
            self.process_ExecutionReport(message=message, sessionId=sessionId)
        elif msgType == fix.MsgType_ExecutionAcknowledgement:
            self.process_ExecutionAcknowledgement(message=message, sessionId=sessionId)
        else:
            print("fromApp unknown msgType {}".format(msgType))

    def toAdmin(self, message, sessionId):
        pass

    def toApp(self, message, sessionId):
        pass

    def init(self, configFile):
        self.configFile = configFile
        self.settings = fix.SessionSettings(self.configFile)
        self.logFactory = fix.ScreenLogFactory(self.settings)
        self.storeFactory = fix.FileStoreFactory(self.settings)
        self.initiator = fix.SocketInitiator(application=self, storeFactory=self.storeFactory,
                                             settings=self.settings,
                                             logFactory=self.logFactory)

    def start(self):
        threading.Thread(target=self.initiator.start()).start()

    def newOrder(self, symbol: str, side: str, qty: float, price: float, account: str, clOrdId: str = None,
                 orderType: str = fix.OrdType_LIMIT):
        message = fix.Message()
        header: fix.Header = message.getHeader()
        header.setField(fix.MsgType(fix.MsgType_NewOrderSingle))
        if clOrdId is None:
            clOrdId = get_next_ClOrdId()

        message.setField(fix.ClOrdID(clOrdId))
        message.setField(fix.Symbol(symbol))
        message.setField(fix.Side(parse_local_side(side)))
        message.setField(fix.OrderQty(qty))
        message.setField(fix.Account(account))
        message.setField(fix.Price(price))

        self.orders[clOrdId] = []
        self.executions[clOrdId] = []
        fix.Session.sendToTarget(message, self.sessionID)

    def process_heart_beat(self, message, sessionId):
        print("process_heart_beat", message)

    def process_ExecutionReport(self, message, sessionId):
        print("process_ExecutionReport", message)
        clOrdId = message.getField(fix.ClOrdID().getField())
        ordStatus = message.getField(fix.OrdStatus().getField())
        print('clOrdId', clOrdId)
        print('executions.keys', self.executions.keys())
        order = self.orders.get(clOrdId, None)
        # self.executions_lock.acquire()
        if clOrdId in list(self.executions.keys()):
            print("clOrdId in executions.keys")
            if ordStatus is not fix.OrdStatus_NEW:
                execution = parse_execution(message)

                execs = self.executions[clOrdId]
                execs.append(execution)
            print(self.executions)
        # self.executions_lock.release()
        if order is not None:
            pass


def process_ExecutionAcknowledgement(self, message, sessionId):
    print("process_ExecutionAcknowledgement", message)


def get_input():
    pass


if __name__ == "__main__":
    configFile = './fix_client_setting'

    settings = fix.SessionSettings(configFile)
    application = FixClient()
    logFactory = fix.ScreenLogFactory(settings)
    storeFactory = fix.FileStoreFactory(settings)
    initiator = fix.SocketInitiator(application=application, storeFactory=storeFactory, settings=settings,
                                    logFactory=logFactory)

    fixClient = threading.Thread(target=initiator.start())

    fixClient.start()

    while True:
        time.sleep(10)
