#!/usr/bin/env python3
import errno
import socket
import simplefix
import threading
import time
from fix_fields import *


class FixClient:
    HOST = '127.0.0.1'  # The server's hostname or IP address
    PORT = 12346  # The port used by the server
    BEGIN_STRING = 'FIX.4.2'
    SENDER = 'BANZAI'
    TARGET = "EXEC"

    buf_read_size = 64
    msg_seq_num = 1
    msg_seq_num_lock = threading.Lock()
    socket_lock = threading.Lock()
    parser = simplefix.FixParser()
    socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __init__(self):
        self.heart_beat_interval = 1

    def read_message(self):
        while True:
            try:
                # print(self.socket_lock.locked())
                self.socket_lock.acquire()
                # buf = self.socket_client.recv(self.buf_read_size)
                buf = self.socket_client.recv(self.buf_read_size)
                self.parser.append_buffer(buf=buf)
                # if len(buf) == 0:
                #     time.sleep(2)
                # else:
                #     time.sleep(1)
            except socket.error as e:
                print(e)
                self.reconnect()
                # A socket error
                pass
            except IOError as e:
                print(e)
                if e.errno == errno.EPIPE:
                    # EPIPE error
                    pass
                else:
                    pass
            # Other error
            except Exception as e:
                print(e)
            finally:
                self.socket_lock.release()
            time.sleep(1)

    def run(self):
        self.reconnect()
        self.send_message(self.log_on_message())
        time.sleep(1)

        # 接收 Server 消息，根据消息类型进行不同回报
        thread_read_message = threading.Thread(target=self.read_message)
        thread_read_message.start()
        thread_parse_message = threading.Thread(target=self.parse_message)
        thread_parse_message.start()
        # time.sleep(10)
        # self.send_message(self.new_order())

    def send_message(self, message: simplefix.FixMessage):
        try:
            print("send:    ", message)
            self.socket_lock.acquire()
            self.socket_client.send(message.encode())
            self.socket_lock.release()
        # except socket.error as e:
        #     # A socket error
        #     pass
        #     print(e)
        # except IOError as e:
        #     print(e)
        #     if e.errno == errno.EPIPE:
        #         # EPIPE error
        #         pass
        #     else:
        #         pass
        # Other error
        except Exception as e:
            print(e)

    def parse_message(self):
        while True:
            try:
                msg_recv = self.parser.get_message()
                if msg_recv is not None:
                    print("receive: ", msg_recv)
                    if msg_recv.get(MsgType) == simplefix.MSGTYPE_HEARTBEAT:
                        # 心跳
                        self.send_message(self.heart_beat_message())
                    elif msg_recv.get(MsgType) == simplefix.MSGTYPE_LOGOUT:
                        # 重新登陆
                        self.msg_seq_num_lock.acquire()
                        self.msg_seq_num = int(msg_recv.get(MsgSeqNum))
                        self.msg_seq_num_lock.release()
                        self.send_message(self.log_on_message())
                    else:
                        pass
            except Exception as e:
                print(e)
            time.sleep(1)

    def log_on_message(self):
        msg = self.basic_message()
        msg.append_pair(HeartBtInt, self.heart_beat_interval, header=True)
        msg.append_pair(MsgType, simplefix.MSGTYPE_LOGON, header=True)

        return msg

    def heart_beat_message(self):
        msg = self.basic_message()
        msg.append_pair(MsgType, simplefix.MSGTYPE_HEARTBEAT, header=True)
        return msg

    def basic_message(self):
        try:
            print("in", self.msg_seq_num_lock.locked())
            self.msg_seq_num_lock.acquire()
            msg = simplefix.FixMessage()
            msg.append_pair(BeginString, self.BEGIN_STRING, header=True)
            msg.append_pair(SenderCompID, self.SENDER, header=True)
            msg.append_pair(TargetCompID, self.TARGET, header=True)
            msg.append_pair(MsgSeqNum, self.msg_seq_num)

            self.msg_seq_num = self.msg_seq_num + 1

            return msg
        finally:
            self.msg_seq_num_lock.release()
            print("out", self.msg_seq_num_lock.locked())

    def new_order(self):
        try:
            self.msg_seq_num_lock.acquire()
            msg = self.basic_message()
            msg.append_pair(MsgType, simplefix.MSGTYPE_NEW_ORDER_SINGLE, header=True)
            msg.append_pair(Symbol, "000725.SZ")
            msg.append_pair(Side, simplefix.SIDE_BUY)
            msg.append_pair(OrderQty, simplefix.SIDE_BUY)
            msg.append_pair(OrdType, simplefix.ORDTYPE_LIMIT)
            msg.append_pair(Price, simplefix.SIDE_BUY)

            return msg
        except Exception as e:
            print(e)
        finally:
            self.msg_seq_num_lock.release()

    def reconnect(self):
        self.socket_client.close()
        self.socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_client.connect((self.HOST, self.PORT))
        pass


if __name__ == "__main__":
    FixClient().run()
