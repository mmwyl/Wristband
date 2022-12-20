# 引入datetime库用于方便时间相关计算
# test upload
from datetime import timedelta
import logging
import voluptuous as vol
import bluepy
import re
import itertools
import threading
# 引入HomeAssitant中定义的一些类与函数
# track_time_interval是监听时间变化事件的一个函数
from homeassistant.helpers.event import track_time_interval
from homeassistant.exceptions import UnknownUser, Unauthorized

from homeassistant.loader import bind_hass
from homeassistant.helpers import intent
from homeassistant.auth.permissions.const import POLICY_CONTROL
from homeassistant.components.group import \
    ENTITY_ID_FORMAT as GROUP_ENTITY_ID_FORMAT
from homeassistant.const import (
    ATTR_ENTITY_ID, SERVICE_TOGGLE, SERVICE_TURN_OFF, SERVICE_TURN_ON,
    STATE_ON)
import homeassistant.helpers.config_validation as cv
import homeassistant.config as config_util
import MyUtil
from bluepy.btle import DefaultDelegate
from bluepy.btle import BTLEException

DOMAIN = "wristband"

scanner = bluepy.btle.Scanner(0)

#定义日志文件 这个方法返回指定的记录
_LOGGER = logging.getLogger(__name__)

CONF_STEP = "step"
DEFAULT_STEP = 3
#扫描间隔
TIME_BETWEEN_UPDATES = timedelta(seconds=30)
from homeassistant.components.wristband import crc_16
import bluepy
import time
# ATTR_GW_MAC = 'gw_mac'
HANDLE_COMMAND = 0x0027
HANDLE_NOTIFY = 0x0028
HANDLE_NOTIFY_3 = 0x002d
HANDLE_002A = 0x002a
HANDLE_NOTIFY_2 = 0x002b
HANDLE_002C = 0x002c
crc16 = crc_16
import os
import json

config_dir = config_util.get_default_config_dir()
CFG_YAML_DIR = os.path.join(os.getcwd(), config_dir)
PATHCFG = CFG_YAML_DIR

async def async_setup(hass, config):
    print("--------start setup Wristband--------")
    list = findingdevice(config[DOMAIN])
    """配置文件加载后，setup被系统调用."""
    # print('\033[1;32m',list,'\033[0m')
    while list.__len__() == 0:
        time.sleep(5)
        list = findingdevice(config[DOMAIN])

    for i in range(len(list)):
        print('\033[1;32m',i + 1, list[i],'\033[0m')
        thread = threading.Thread(target=WristbandState, args=(hass, list[i]))
        thread.setName(list[i]['macAddress'])
        thread.setDaemon(True)
        thread.start()

    return True

'''用蓝牙扫描发现周围设备'''
def findingdevice (mac_list):
    print('-----start scan-----')
    devices = scanner.scan(5)
    wirstList=[]
    config_device = []
    for item in mac_list:
        config_device.append(item['mac'])
    for device in devices:
        try:
            model = next(itertools.filterfalse(lambda x: x[0] != 9, device.getScanData()))[2] #手环名字
            Manufacturer = next(itertools.filterfalse(lambda x: x[0] != 255,device.getScanData( )))[2]
            #广播,每十分钟更新一次  返回常用数值    如:107803e842724b001b110000c000c01e8001
            print('-----', str(Manufacturer), model)
        except:
            continue
        if not re.search('^P3A', model):
            continue
        if device.addr in config_device:
            data = interp_resp_hex_by_2(str(Manufacturer))
            HR = int(bytes.fromhex(data[4]).hex(), 16)
            SBP = int(bytes.fromhex(data[5]).hex(), 16)
            DBP = int(bytes.fromhex(data[6]).hex(), 16)
            SO2 = int(bytes.fromhex(data[7]).hex(), 16)
            step = str(data[9]) + str(data[10]) + str(data[11])
            STEP = int(bytes.fromhex(step).hex(), 16)

            #组装state数据
            wirstList.append({"friendly_name":model,"macAddress": device.addr,"SBPbloodPressure":SBP,"DBPbloodPressure":DBP,"Heartrate":HR, "Equipmenttype":"","Blood oxygen":SO2,"Respiratoryrate":"","ECG":"","Stepnumber":STEP,"sleep":""})
    return wirstList

def interp_resp_hex_by_2(str):
    '''
    按字节分解返回值
    返回一个list，用于分析
    :param str:
    :return:
    '''
    index = 0
    list = []
    while not index == len(str):
        list.append(str[index:index + 2])
        index += 2
    return list


iii = 0
total_pkg = 0
data_test = []
final_data = ""
isFinishWrite = False

'''write to log file'''
def write2log(list_data):
    if not os.path.exists("/root/.homeassistant/wristband_return_data.log"):
        os.remove("/root/.homeassistant/wristband_return_data.log")

    f = open("/root/.homeassistant/wristband_return_data.log", 'w')
    f.close()
    handler = logging.FileHandler(filename='/root/.homeassistant/wristband_return_data.log')
    _LOGGER.setLevel(logging.DEBUG)
    handler.setLevel(logging.DEBUG)
    _LOGGER.addHandler(handler)
    log = json.dumps(list_data)
    _LOGGER.info(log)

    global isFinishWrite
    isFinishWrite = True

class MyNotifyDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        global final_data
        if str(cHandle) == "39":
            # MyUtil.print_with_green("notify from " + str(cHandle) + "---" + str(data.hex()) + "\n")
            temp = interp_resp_hex_by_2(str(data.hex()))
            if temp[0] == "05":
                if str(data.hex()).__contains__("05800c00"):
                    # print(final_data)
                    time.sleep(0.1)
                    write2log(final_data)
                    final_data = ""
                else:
                    if temp[4] == "00" and temp[5] == "00":
                        final_data = ""
                        write2log(str(data.hex()))
                    else:
                        if temp[1] in ["40","41","42","43","44"]:
                            final_data = ""
                            write2log(str(data.hex( )))
                        else:
                            global total_pkg
                            total_pkg = int(bytes.fromhex(temp[9] + temp[8] + temp[7] + temp[6]).hex( ), 16)
                            total_record = int(bytes.fromhex(temp[5] + temp[4]).hex( ), 16)
                            total_byte = int(bytes.fromhex(temp[13] + temp[12] + temp[11] + temp[10]).hex( ), 16)
                            MyUtil.print_with_green(total_record)
                            MyUtil.print_with_green(total_pkg)
                            MyUtil.print_with_green(total_byte)

            else:
                final_data = ""
                write2log(str(data.hex()))
        if str(cHandle) == "44":
            global iii
            iii += 1
            print(iii)
            if iii == 1:
                final_data += str(data.hex())[0:-4]
            else:
                final_data += str(data.hex())[8:-4]
        MyUtil.print_with_green("notify from " + str(cHandle) + "---" + str(data.hex()) + "\n")

            # print("time of second")
            # print(int(bytes.fromhex(data_list[7] + data_list[6] + data_list[5] + data_list[4]).hex(), 16))
            # data_test.append(temp)
            # pass
        # print("notify from " + str(cHandle) + "---" + str(data.hex()) + "\n")

class WristbandState(object):
    """定义一个类，此类中存储了状态与属性值，并定时更新状态."""
    def __init__(self,hass, attr):
        self._hass = hass
        # self._step = step
        self._attr = attr
        self._state = 0
        self.peri = bluepy.btle.Peripheral()
        self.peri.setDelegate(MyNotifyDelegate())
        # 在类初始化的时候，设置初始状态,将手环数据在state中显示出来
        self._hass.states.async_set(DOMAIN + "." + re.sub('\s+', '', self._attr["friendly_name"]).replace(" ", "_"),
                              re.sub('\s+', '', self._attr["friendly_name"]).replace(" ", "_"), attributes=self._attr)

        def async_wristband_state(service):
            _LOGGER.info("wristband's async_wristband_state service is called")
            global isFinishWrite
            global iii
            global total_pkg
            total_pkg = 0
            iii = 0
            isFinishWrite = False
            params = service.data.copy()
            params.pop(ATTR_ENTITY_ID, None)
            request_count = 0


            try:
                self.peri.writeCharacteristic(HANDLE_NOTIFY, b'\x02\x00')
                self.peri.writeCharacteristic(HANDLE_NOTIFY_2, b'\x02\x00')
                self.peri.writeCharacteristic(HANDLE_NOTIFY_3, b'\x02\x00')
                self.test_send_request( bytes.fromhex(str(params["command"])).hex())

            except:
                write2log("ffff")
                return

            while not isFinishWrite:
                print("wait to finish writing")
                if request_count == 2:
                    write2log("ffff")
                    return
                try:
                    if (self.peri.waitForNotifications(1)):
                        continue
                    else:
                        request_count += 1
                        print("non notify : ", request_count)
                        time.sleep(1)
                        continue
                except:
                    request_count += 1
                    print("except plus 1 = :" , request_count)
                    time.sleep(1)
                    continue

        hass.services.async_register(DOMAIN, 'async_wristband_state', async_wristband_state)
        #每隔一段时间，更新一下实体的状态
        track_time_interval(self._hass, self.update, TIME_BETWEEN_UPDATES)

        while True:
            print('\033[1;31m try to connect --',self._attr['friendly_name'],'\033[0m')
            try:
                self.peri.setDelegate(MyNotifyDelegate())
                self.peri.connect(self._attr["macAddress"], bluepy.btle.ADDR_TYPE_RANDOM)
            except:
                time.sleep(3)
                continue
            while not self.peri.getState().__eq__('conn'):
                time.sleep(1)

            print('\033[1;32m connected -----', self._attr['friendly_name'], ' \033[0m')
            self.peri.writeCharacteristic(HANDLE_NOTIFY, b'\x02\x00')
            self.peri.writeCharacteristic(HANDLE_NOTIFY_2, b'\x02\x00')
            self.peri.writeCharacteristic(HANDLE_NOTIFY_3, b'\x02\x00')
            self.init_wristband_setup()
            while True:
                time.sleep(10)
                try:
                    if not str(self.peri.getState()) == "conn":
                        MyUtil.print_with_red("---disconnected!!!---")
                        break
                except:
                    MyUtil.print_with_red("---disconnected!!! by EXCEPTION---")
                    self.peri.disconnect()
                    time.sleep(10)
                    break
            # try:
            #     while self.peri.getState().__eq__("conn"):
            #         time.sleep(3)
            # except:
            #     self.peri.disconnect()
            #     time.sleep(3)

    def update(self,now):
        """在WristbandStateState类中定义函数update,更新状态."""
        MyUtil.print_with_33("-----WristbandState is updatingi-----")
        #状态值每次增加step
        # self._state = self._state + self._step
        #设置新的状态值
        self._hass.states.async_set(DOMAIN + "." + re.sub('\s+', '', self._attr["friendly_name"]).replace(" ", "_"),
                               re.sub('\s+', '', self._attr["friendly_name"]).replace(" ", "_"), attributes=self._attr)

    def test_send_request(self, command):
        command_hex = bytes.fromhex(command)
        # self.peri.writeCharacteristic(HANDLE_NOTIFY, b'\x02\x00')
        # self.peri.writeCharacteristic(HANDLE_NOTIFY_3, b'\x02\x00')
        crc = crc16.crc_16(command_hex)
        crc_b = bytes.fromhex(crc)
        tx_value = command_hex + crc_b
        print('发送请求---------')
        self.peri.writeCharacteristic(HANDLE_COMMAND, tx_value, withResponse=False)
        info = str((self.peri.readCharacteristic(HANDLE_COMMAND)).hex())
        return info

    '''初始化手环，如果需要的话'''
    def init_wristband_setup(self):
        '''初始化代码'''
        # self.test_send_request("03090900 00 00 00")
        # time.sleep(0.5)
        # self.test_send_request("03090900 00 01 00")
        # time.sleep(0.5)
        # self.test_send_request("03090900 00 02 00")
        # time.sleep(0.5)
        # self.test_send_request("03090900 00 03 00")
        # time.sleep(0.5)
        # self.test_send_request("03090900 00 04 00")
        # time.sleep(0.5)
        # self.test_send_request("03090900 00 05 00")
        # time.sleep(0.5)
        # self.test_send_request("03090900 00 06 00")
        # time.sleep(0.5)
        # self.test_send_request("010c0800 01 3c")
        print('-------finish init-----------')



