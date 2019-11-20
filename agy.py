# usage: python stream_acc.py [mac1] [mac2] ... [mac(n)]
from __future__ import print_function
from mbientlab.metawear import MetaWear, libmetawear, parse_value
from mbientlab.metawear.cbindings import *
from time import sleep
from threading import Event

import platform
import sys
import socket
import time

if sys.version_info[0] == 2:
    range = xrange

# curl ifconfig.me    
TCP_IP = '192.168.0.101'
TCP_PORT = 5010
BUFFER_SIZE = 1024  # Normally 1024, but we want fast response

#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s = socket.socket()
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

conn, addr = s.accept()
print("Connection from " + str(addr))

class State:
    def __init__(self, connection, device):
        self.device = device
        self.connection = connection
        self.samples = 0
        self.acallback = FnVoid_VoidP_DataP(self.data_ahandler)
        self.gcallback = FnVoid_VoidP_DataP(self.data_ghandler)

    def data_ahandler(self, ctx, data):
        msg = parse_value(data)
        if(self.samples == 1000):
            self.samples = 0
        else:
            self.samples+= 1
            #print("%s -> %s" % (self.device.address, msg))
        self.connection.send("A"+str(msg))
        #self.connection.send(time.asctime(time.localtime(time.time())))

    def data_ghandler(self, ctx, data):
        msg = parse_value(data)
        if(self.samples == 1000):
            self.samples = 0
        else:
            self.samples+= 1
            #print("%s -> %s" % (self.device.address, msg))
        self.connection.send("G"+str(msg))
        #self.connection.send(time.asctime(time.localtime(time.time())))
       

mach = 'cd:ab:4d:bd:aa:b7'
d = MetaWear(mach)
d.connect()
print("Connected to " + d.address)
s=State(conn, d)
print("Configuring device")
libmetawear.mbl_mw_settings_set_connection_parameters(s.device.board, 7.5, 7.5, 0, 6000)
sleep(3.5)

libmetawear.mbl_mw_acc_set_odr(s.device.board, 10.0)
#libmetawear.mbl_mw_acc_set_odr(s.device.board, 1.0)
libmetawear.mbl_mw_acc_set_range(s.device.board, 16.0)
libmetawear.mbl_mw_acc_write_acceleration_config(s.device.board)

# 6=25 7=50  i=25*2^(i-6)
libmetawear.mbl_mw_gyro_bmi160_set_odr(s.device.board, 6)
#libmetawear.mbl_mw_gyro_bmi160_set_odr(s.device.board, 1.0)
libmetawear.mbl_mw_gyro_bmi160_set_range(s.device.board, 16)
libmetawear.mbl_mw_gyro_bmi160_write_config(s.device.board)


asignal = libmetawear.mbl_mw_acc_get_acceleration_data_signal(s.device.board)
libmetawear.mbl_mw_datasignal_subscribe(asignal, None, s.acallback)

gsignal = libmetawear.mbl_mw_gyro_bmi160_get_rotation_data_signal(s.device.board)
libmetawear.mbl_mw_datasignal_subscribe(gsignal, None, s.gcallback)


libmetawear.mbl_mw_acc_enable_acceleration_sampling(s.device.board)
libmetawear.mbl_mw_acc_start(s.device.board)

libmetawear.mbl_mw_gyro_bmi160_enable_rotation_sampling(s.device.board)
libmetawear.mbl_mw_gyro_bmi160_start(s.device.board)


sleep(36000.0)

libmetawear.mbl_mw_acc_stop(s.device.board)
libmetawear.mbl_mw_acc_disable_acceleration_sampling(s.device.board)

libmetawear.mbl_mw_gyro_bmi160_stop(s.device.board)
libmetawear.mbl_mw_gyro_bmi160_disable_rotation_sampling(s.device.board)


asignal = libmetawear.mbl_mw_acc_get_acceleration_data_signal(s.device.board)
libmetawear.mbl_mw_datasignal_unsubscribe(asignal)

gsignal = libmetawear.mbl_mw_gyro_bmi160_get_rotation_data_signal(s.device.board)
libmetawear.mbl_mw_datasignal_unsubscribe(gsignal)


libmetawear.mbl_mw_debug_disconnect(s.device.board)

print("Total Samples Received")
print("%s -> %d" % (s.device.address, s.samples))

conn.close()
