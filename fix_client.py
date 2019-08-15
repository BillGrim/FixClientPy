import quickfix
import sys
import threading

class FixClient(quickfix.Application):
    def onCreate(self, session):
        pass

    def onLogon(self, session):
        pass

    def onLogout(self, session):
        pass

    def fromAdmin(self, session, message):
        pass

    def fromApp(self, session, message):
        pass

    def toAdmin(self, session, message):
        pass

    def toApp(self, session, message):
        pass


if __name__ == "__main__":
    configFile = 'fix_client_setting'

    settings = quickfix.SessionSettings(configFile)
    application = FixClient()
    logFactory = quickfix.ScreenLogFactory(settings)
    storeFactory = quickfix.FileStoreFactory(settings)
    initiator = quickfix.SocketInitiator(application=application, storeFactory=storeFactory, settings=settings)

    fixClient = threading.Thread(target=initiator.start())

