import time

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.widget import Widget
import fix_client


class GUI(Widget):
    pass


class FixClientGUI(App):
    def build(self):
        return GUI()


if __name__ == "__main__":
    configFile = './fix_client_setting'
    client = fix_client.FixClient()
    client.init(configFile)
    client.start()
    while not client.is_ready():
        time.sleep(1)
        pass
    client.newOrder("000725.SZ", 'B', 1000, 3, 'wcq')
    FixClientGUI().run()
