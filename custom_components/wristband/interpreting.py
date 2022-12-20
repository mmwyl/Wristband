import re
#coding=utf-8
import time
import json

result_success = 'success'
result_fail = 'fail'

'''主要解析函数'''
def interpret_command(request_command,response_command,timeout=3):
    request = split_by_2(request_command)
    response = split_by_2(response_command)
    # print(">>>request>>>", request)
    # print(">>>request>>>>>>>>", type(request))
    # print(">>>response>>>>>", response)
    # print(">>>response>>>>>>>>", type(response))
    count = 0
#    while not request[0:2] == response[0:2]:
#        if not count == timeout:
#            time.sleep(1)
#            count += 1
#            continue
#        return 'request time out'
#     if response[2] == "07":
#         if response[-3] in ["fb","fc","fd","fe","ff"]:
#             resp = check_fail(response)
#             return resp
    if response[0] == '00':
        resp = interpret_00(split_by_2(response_command))
    elif response[0] == '01':
        resp = interpret_01(split_by_2(response_command))
    elif response[0] == '02':
        resp = interpret_02(split_by_2(response_command))
    elif response[0] == '03':
        resp = interpret_03(split_by_2(response_command))
    elif response[0] == '04':
        resp = interpret_04(split_by_2(response_command))
    elif response[0] == '05':
        resp = interpret_05(split_by_2(response_command))
    elif response[0] == '06':
        resp = interpret_06(split_by_2(response_command))
    elif response[0] == '07':
        resp = interpret_07(split_by_2(response_command))
    elif response[0] == response[1] == "ff":
        temp = {}
        temp["result"] = "fail"
        temp["resultdata"] = ""
        temp["resultmsg"] = "获取异常，请重试"
        resp = temp
    else:
        resp = '手环返回值错误'
    return resp

'''分离字节信息'''
def split_by_2(str):
    '''
    按字节分解返回值
    返回一个list，用于分析
    :param str:
    :return list:
    '''
    index = 0
    list = []
    while not index == len(str):
        list.append(str[index:index + 2])
        index += 2
    return list

'''成功/失败返回值字典'''
def generate_dict_return(issuccess,msg):
    '''
    :param issuccess:
    :param msg:
    :return dict:
    '''
    dict = {}
    if issuccess == 0:
        dict['result'] = 'fail'
    elif issuccess == 1:
        dict['result'] = 'success'

    dict['resultdata'] = ''
    dict['resultmessage'] = msg
    return dict

'''操作指令返回解析'''
def order_command(command_list):
    '''
    :param command_list:
    :return dict:
    '''
    if command_list[-3] == '00':
        return generate_dict_return(1,'设置成功')
    elif command_list[-3] == '01':
        return generate_dict_return(0, '设置失败，参数错误')
    else:
        return check_fail(command_list)

'''操作指令返回解析 type2'''
def order_command_2(command_list):
    '''
    :param command_list:
    :return dict:
    '''
    if command_list[-3] == '00':
        return generate_dict_return(1,'设置成功')
    elif command_list[-3] == '01':
        return generate_dict_return(0, '设置失败，模式不支持')
    else:
        return check_fail(command_list)

'''操作指令返回解析 type3'''
def order_command_3(command_list):
    '''
    :param command_list:
    :return dict:
    '''
    if command_list[-3] == '00':
        return generate_dict_return(1,'成功')
    elif command_list[-3] == '01':
        return generate_dict_return(0, '失败，类别不支持')
    else:
        return check_fail(command_list)

'''16to10转换'''
def hex2int2str(hex_str):
    hex_var = bytes.fromhex(hex_str).hex()
    int_var = int(hex_var,16)
    str_var = str(int_var)
    return str_var

'''16to2转换'''
def hex2int_2(hex_str):
    hex_var = bytes.fromhex(hex_str).hex()
    bin_var = bin(int(hex_var, 16))
    str_var = str(bin_var)
    return str_var

'''固件升级（00）返回值解析'''
def interpret_00(command_list):
    resp = {}
    if command_list[1] == '00':
        if command_list[-3] == '00':
            resp = generate_dict_return(1,'成功进入固件升级模式')
        elif command_list[-3] == '01':
            resp = generate_dict_return(0, '电量过低')
        elif command_list[-3] == '02':
            resp = generate_dict_return(0, '设备不支持')
    elif command_list[1] == '01':
        #解析起来过于冗长，并用不到这个返回值，暂不解析
        resp = generate_dict_return(0, '通过本协议配套App升级')
    return resp

'''设置命令（01）返回值解析'''
def interpret_01(command_list):
    resp = {}
    if command_list[1] in ['00','03','04','05','07','0a','0b','0c','0d','0e','0f','10','11','12','13','14','15','16','17','18']:
        '''
        时间设置，用户信息设置，单位设置，久坐提醒设置，防丢提醒参数设置，通知提醒开关设置，心率报警设置，心率监测模式设置，
        找手机开关设置，恢复出厂设置，勿扰模式设置，ANCS 开关设置，有氧教练设置，语言设置，抬腕亮屏开关设置， 
        显示屏亮度设置，肤色设置，血压范围设置，设置设备蓝牙名称
        '''
        resp = order_command(command_list)

    elif command_list[1] in ['06','08','09']:
        '''
        防丢提醒 , 左右手佩戴设置 , 手机操作系统设置
        '''
        resp = order_command_2(command_list)

    elif command_list[1] == '01':               #闹钟设置
        if command_list[4] == '00':
            resp = inquiry_remainder(command_list)
        elif command_list[4] == '01':
            resp = set_remainder_command(command_list)
        elif command_list[4] == '02':
            resp = delete_remainder_command(command_list)
        elif command_list[4] == '02':
            resp = edit_remainder_command(command_list)
    elif command_list[1] == '02':               #目标设置
        if command_list[-3] == '00':
            resp = generate_dict_return(1,'设置成功')
        elif command_list[-3] == '01':
            resp = generate_dict_return(0,'设置失败，类型不支持')
        elif command_list[-3] == '02':
            resp = generate_dict_return(0,'设置失败，参数错误')
    return resp

'''获取指令（02）返回值解析'''
def interpret_02(command_list):
    resp = {}
    if command_list[1] == '00':
        resp['result'] = 'success'
        resp['resultdata'] = get_device_info(command_list[4:12])
        resp['resultmessage'] = '获取设备基本信息'
    elif command_list[1] == '01':
        resp['result'] = 'success'
        resp['resultdata'] = '' #get_device_support_function(command_list[4:12])
        resp['resultmessage'] = '获取设备基本信息'
    elif command_list[1] == '02':
        resp['result'] = 'success'
        resp['resultdata'] = get_MAC(command_list[4:10])
        resp['resultmessage'] = '获取设备MAC地址'
    elif command_list[1] == '03':
        resp['result'] = 'success'
        resp['resultdata'] = "P3A PLUS"   #全都返回同一个值，bug
        resp['resultmessage'] = '获取设备名称或型号信息'
    elif command_list[1] == '04':
        resp['result'] = 'success'
        resp['resultdata'] = ""   #返回值错误，无法解析
        resp['resultmessage'] = '获取设备功能开关状态'
    elif command_list[1] == '05':
        resp['result'] = 'success'
        resp['resultdata'] = get_HR(command_list[-4:-2])
        resp['resultmessage'] = '获取当前心率'
    elif command_list[1] == '06':
        resp['result'] = 'success'
        resp['resultdata'] = get_BP(command_list[-5:-2])
        resp['resultmessage'] = '获取当前血压'
    elif command_list[1] == '07':
        resp['result'] = 'success'
        resp['resultdata'] = get_user_config(command_list) #用户配置
        resp['resultmessage'] = '获取用户配置'
    elif command_list[1] == '08':
        resp['result'] = 'success'
        resp['resultdata'] = '' #获取设备LOG，尚未使用该功能
        resp['resultmessage'] = '获取设备LOG'
    return resp

'''APP控制指令（03）返回值解析'''
def interpret_03(command_list):
    resp = {}
    if command_list[1] == '00':
        resp['result'] = 'success'
        resp['resultdata'] = ''
        resp['resultmessage'] = '寻找手环成功'
    elif command_list[1] in ['01','02','04','05','10','11']:
        '''
        心率测试开关控制, 血压测试开关控制, APP 退出通知指令, 有氧教练模式开关控制
        '''
        resp = order_command(command_list)
    elif command_list[1] == '03':
        resp = correct_BP_command(command_list)
    elif command_list[1] == '06':
        if command_list[-3] == '00':
            resp = generate_dict_return(1, '绑定成功')
        elif command_list[-3] == '01':
            resp = generate_dict_return(0, '绑定失败,系统类型不支持')
        elif command_list[-3] == '02':
            resp = generate_dict_return(0, '绑定失败,设备已绑定')
    elif command_list[1] == '07':
        if command_list[-3] == '00':
            resp = generate_dict_return(1, '解绑成功')
        elif command_list[-3] == '01':
            resp = generate_dict_return(0, '解绑失败,参数错误')
        elif command_list[-3] == '02':
            resp = generate_dict_return(0, '解绑失败,设备未绑定')
    elif command_list[1] in ['08','09','0b','0c','0e']:
        '''
        信息醒命令, 实时数据上传控制, 波形上传控制, 运动模式启动/停止, 相机拍照控制
        自定义采样率启动/停止心率测量,
        '''
        resp = order_command_3(command_list)
    elif command_list[1] == '0a':
        if command_list[-3] == command_list[-4] == 0:
            resp = generate_dict_return(0,'类型不支持')
        else:
            resp['result'] = 'success'
            resp['resultdata'] = str(int(bytes.fromhex(command_list[-4]+command_list[-3]).hex(),16))
            resp['resultmessage'] = '成功'
    elif command_list[1] == '12' or command_list[1] == '13':
        if command_list[-3] == '00':
            resp = generate_dict_return(1, '发送成功')
        elif command_list[-3] == '01':
            resp = generate_dict_return(0, '发送失败，类型错误')
    elif command_list[1] == '14':
        temp = {}
        temp['electrode'] = '心电电极脱落' if command_list[4] == '00' else '心电电极接触良好'
        temp['photoelectric'] = '未佩戴' if command_list[5] == '00' else '已佩戴'
        resp['result'] = 'succuess'
        resp['resultdata'] = temp
        resp['resultmessage'] = '成功'
    return resp

'''设备控制指令(04)返回值解析'''
def interpret_04(command_list):
    resp = {}
    resp = order_command_3(command_list)
    return resp

'''同步健康数据返回值解析'''
def interpret_05(command_list):
    resp = {}
    data_list = []
    new_list = command_list[4:]
    if command_list[1] == "18":
        data_list = interpret_healthy_history(new_list)
        resp["result"] = "success"
        resp["resultdata"] = data_list
        resp["resultmessage"] = "获取历史健康数据成功"
    elif command_list[1] == "11":
        data_list = interpret_sport_history(new_list)
        resp["result"] = "success"
        resp["resultdata"] = data_list
        resp["resultmessage"] = "获取历史运动数据成功"
        pass
    elif command_list[1] == "13":
        data_list = interpret_sleep_history(new_list)
        resp["result"] = "success"
        resp["resultdata"] = data_list
        resp["resultmessage"] = "获取历史睡眠数据成功"
        pass
    elif command_list[1] == "15":
        data_list = interpret_heartrate_history(new_list)
        resp["result"] = "success"
        resp["resultdata"] = data_list
        resp["resultmessage"] = "获取历史心率数据成功"
        pass
    elif command_list[1] in ["40","41","42","43",]:
        if command_list[4] == "00":
            resp["result"] = "success"
            resp["resultdata"] = {}
            resp["resultmessage"] = "删除率数据成功"
        elif command_list == "01":
            resp["result"] = "fail"
            resp["resultdata"] = {}
            resp["resultmessage"] = "删除率数据失败"
        else:
            resp["result"] = "success"
            resp["resultdata"] = {}
            resp["resultmessage"] = "无数据"
        pass
    elif command_list[1] == "44":
        if command_list[4] == "00":
            resp["result"] = "success"
            resp["resultdata"] = {}
            resp["resultmessage"] = "删除率数据成功"
        else:
            resp["result"] = "fail"
            resp["resultdata"] = {}
            resp["resultmessage"] = "删除率数据失败"
    else:
        if command_list[2] == "08" and command_list[4] == "00" and command_list[5] == "00":
            resp["result"] = "success"
            resp["resultdata"] = []
            resp["resultmessage"] = "暂无历史数据成功"
        else:
            resp = "bad_data"
    return resp

'''设备实时数据上传返回值解析'''
def interpret_06(command_list):
    resp = {}
    return resp

'''历史采集数据同步返回值解析'''
def interpret_07(command_list):
    resp = {}
    return resp


def interpret_heartrate_history(command_list):
    data_list = []
    record = len(command_list) / 6
    print(record)
    i = 0
    while i < int(record):
        temp_resp = {}
        temp_resp["updatetime"] = convertTimeStamp(command_list[0 + (i * 6):4 + (i * 6)])
        if command_list[4] == "00":
            temp_resp["type"] = "单次模式"
        elif command_list[4] == "01":
            temp_resp["type"] = "监测模式"
        elif command_list[4] == "02":
            temp_resp["type"] = "有氧教练模式"
        temp_resp["heartrate"] = int(bytes.fromhex(command_list[5 + (i * 6)]).hex(), 16)
        data_list.append(temp_resp)
        i += 1

    return data_list



'''解析历史运动数据'''
def interpret_sport_history(command_list):
    data_list = []
    record = len(command_list) / 14
    print(record)
    i = 0
    while i < int(record):
        temp_resp = {}
        temp_resp["starttime"] = convertTimeStamp(command_list[0 + (i * 14):4 + (i * 14)])
        temp_resp["endtime"] = convertTimeStamp(command_list[4 + (i * 14):8 + (i * 14)])
        temp_resp["step"] = int(bytes.fromhex(command_list[9 + (i * 14)] + command_list[8 + (i * 14)]).hex(), 16)
        temp_resp["distance"] = int(bytes.fromhex(command_list[11 + (i * 14)] + command_list[10 + (i * 14)]).hex(), 16)
        temp_resp["calories"] = int(bytes.fromhex(command_list[13 + (i * 14)] + command_list[12 + (i * 14)]).hex(), 16)
        data_list.append(temp_resp)
        i += 1
    return data_list

'''解析历史睡眠数据'''
def interpret_sleep_history(command_list):
    return_list = []
    data_list = []
    total_bytes = int(bytes.fromhex(command_list[3] + command_list[2]).hex(), 16)
    while not total_bytes == len(command_list):
        data_list.append(command_list[0:total_bytes])
        command_list = command_list[total_bytes:]
        total_bytes = int(bytes.fromhex(command_list[3] + command_list[2]).hex(), 16)
    else:
        data_list.append(command_list)
    for item in data_list:
        record = {}
        record["sleeptime"] = convertTimeStamp(item[4 :8])
        record["sleepperiod"] = int(bytes.fromhex(item[11] + item[10] + item[9] + item[8]).hex(), 16) - int(bytes.fromhex(item[7] + item[6] + item[5] + item[4]).hex(), 16)
        record["awaketime"] = convertTimeStamp(item[8 :12])
        record["awakenum"] = 0
        record["deepsleep"] = int(bytes.fromhex(item[17] + item[16]).hex(), 16) * 60
        record["lightsleep"] = int(bytes.fromhex(item[19] + item[18]).hex(), 16) * 60
        record["deepsleepperiod"], record["lightsleepperiod"] = interpret_deep_light_sleep(item[20:])
        return_list.append(record)
    return return_list

'''解析深睡浅睡数据'''
def interpret_deep_light_sleep(command_list):
    deep_list = []
    light_list = []
    record = len(command_list) / 8
    i = 0
    while i < int(record):
        temp_resp = {}
        temp_resp["starttime"] = convertTimeStamp(command_list[1 + (i * 8):5 + (i * 8)])
        temp_resp["period"] = int(bytes.fromhex(command_list[7]+command_list[6]+command_list[5]).hex(), 16)
        temp_resp["endtime"] = convertTimeStamp(command_list[1 + (i * 8):5 + (i * 8)],int(temp_resp["period"]))
        if command_list[0 + (i * 8)] == "f1":
            deep_list.append(temp_resp)
        else:
            light_list.append(temp_resp)
        i += 1
    return json.dumps(deep_list), json.dumps(light_list)

'''解析历史健康数据'''
def interpret_healthy_history(command_list):
    data_list = []
    record = len(command_list) / 20
    print(record)
    i = 0
    while i < int(record):
        temp_resp = {}
        temp_resp["updatetime"] = convertTimeStamp(command_list[0 + (i * 20):4 + (i * 20)])
        temp_resp["heartrate"] = int(bytes.fromhex(command_list[6 + (i * 20)]).hex(), 16)
        bp = {}
        bp["Systolic"] = int(bytes.fromhex(command_list[7 + (i * 20)]).hex(), 16)
        bp["Diastolic"] = int(bytes.fromhex(command_list[8 + (i * 20)]).hex(), 16)
        temp_resp["bloodpressure"] = json.dumps(bp)
        temp_resp["bloodoxygen"] = int(bytes.fromhex(command_list[9 + (i * 20)]).hex(), 16)
        temp_resp["respiratoryrate"] = int(bytes.fromhex(command_list[10 + (i * 20)]).hex(), 16)
        temp_resp["hrv"] = int(bytes.fromhex(command_list[11 + (i * 20)]).hex(), 16)
        temp_resp["cvrr"] = int(bytes.fromhex(command_list[12 + (i * 20)]).hex(), 16)
        data_list.append(temp_resp)
        i += 1
    return data_list

'''时间戳转换'''
def convertTimeStamp(command_list, addition_time = None):
    timeStamp_2000 = int(bytes.fromhex(command_list[3] + command_list[2] + command_list[1] + command_list[0]).hex(), 16)
    dt = '2000-01-01 00:00:00'
    ts = int(time.mktime(time.strptime(dt, "%Y-%m-%d %H:%M:%S")))
    total_timestamp = timeStamp_2000 + ts
    date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(total_timestamp))
    if addition_time is not None:
        date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(total_timestamp + addition_time))
    return date

'''查询闹钟'''
def inquiry_remainder(command_list):
    remainder_list = []
    resp = {}
    if command_list[6] == '00':
        resp = generate_dict_return(1,'尚无闹钟，请添加')
    else:
        while not len(command_list) == 9:
            remainder_list.append(getremainder(command_list[7:12]))
            del command_list[7:12]
        resp['result'] = 1
        resp['resultdata'] = remainder_list
        resp['resultmessage'] = '查询完毕'
    return resp

'''解析提醒函数'''
def getremainder(byteslist):
    remainder = {}

    if byteslist[0] == '00':
        remainder['type'] = '起床'
    elif byteslist[0] == '01':
        remainder['type'] = '睡觉'
    elif byteslist[0] == '02':
        remainder['type'] = '锻炼'
    elif byteslist[0] == '03':
        remainder['type'] = '吃药'
    elif byteslist[0] == '04':
        remainder['type'] = '约会'
    elif byteslist[0] == '05':
        remainder['type'] = '聚会'
    elif byteslist[0] == '06':
        remainder['type'] = '会议'
    else:
        remainder['type'] = '自定义'

    remainder['time'] = hex2int2str(byteslist[1])+":"+hex2int2str(byteslist[2])

    return remainder

'''set remainder return'''
def set_remainder_command(command_list):
    resp = {}
    if command_list[-3] == '00':
        resp = generate_dict_return(1,'设置成功')
    elif command_list[-3] == '01':
        resp = generate_dict_return(0,'设置失败，超过设备闹钟最大数')
    elif command_list[-3] == '02':
        resp = generate_dict_return(0, '此闹钟已存在')
    elif command_list[-3] == '03':
        resp = generate_dict_return(0,'类型不支持')
    elif command_list[-3] == '04':
        resp = generate_dict_return(0,'参数错误')
    return resp

'''delete remainder return'''
def delete_remainder_command(command_list):
    resp = {}
    if command_list[-3] == '00':
        resp = generate_dict_return(1, '删除成功')
    elif command_list[-3] == '01':
        resp = generate_dict_return(0, '删除失败，闹钟不存在')
    elif command_list[-3] == '02':
        resp = generate_dict_return(0, '删除失败，参数错误')
    return resp

'''edit remainder return'''
def edit_remainder_command(command_list):
    resp = {}
    if command_list[-3] == '00':
        resp = generate_dict_return(1, '修改成功')
    elif command_list[-3] == '01':
        resp = generate_dict_return(0, '修改失败，此闹钟不存在')
    elif command_list[-3] == '02':
        resp = generate_dict_return(0, '修改失败，修改的闹钟已存在')
    elif command_list[-3] == '03':
        resp = generate_dict_return(0, '修改失败，参数错误')
    return resp

'''get device information获取设备基本信息'''
def get_device_info(command):
    dict_device = {}
    dict_device['id'] = command[1] + command[0]
    dict_device['version'] = command[2:4]  #字版本在前，主版本在后
    if command[4] == '00':
        dict_device['battery_state'] = '正常'
    elif command[4] == '01':
        dict_device['battery_state'] = '低电量'
    elif command[4] == '02':
        dict_device['battery_state'] = '充电中'
    elif command[4] == '03':
        dict_device['battery_state'] = '充满'
    dict_device['battery_level'] = hex2int2str(command[5])
    dict_device['bind_state'] = '未绑定' if command[6]=='00' else '已绑定'
    dict_device['update_state'] = '无需同步' if command[6]=='00' else '需同步'
    return dict_device

'''get device support function 获取设备支持功能列表'''
def get_device_support_function(command):
    '''
    稍后在写
    功能将会改动，暂时不需要解析这个指令
    '''

'''get MAC address'''
def get_MAC(command):
    resp = {}
    resp['mac'] = command[-1] + ":" + command[-2] + ":" + command[-3] + ":" + command[-4] + ":" +command[-5] + ":" + command[-6]
    # command.reverse()
    # mac_addr = ''
    # for i in command:
    #     mac_addr += i
    #     mac_addr += ':'
    # del mac_addr[-1]
    # resp['mac'] = mac_addr
    return resp

'''get current HR'''
def get_HR(command):
    resp = {}
    resp['state'] = '正在测心率' if command[0] == '01' else '未测心率'
    resp['hr'] = hex2int2str(command[1])
    return resp

'''get current BP'''
def get_BP(command):
    resp = {}
    resp['state'] = '正在测血压' if command[0] == '01' else '未测血压'
    resp['Systolic'] = hex2int2str(command[1])  #高压
    resp['Diastolic'] = hex2int2str(command[2]) #低压
    return resp

'''血压校准命令返回值'''
def correct_BP_command(command):
    if command[-3] == '00':
        return generate_dict_return(1, '校准成功')
    elif command[-3] == '01':
        return generate_dict_return(0, '校准失败，参数错误')
    elif command[-3] == '02':
        return generate_dict_return(0, '校准失败，设备未正在测试血压或者血压还没有出值')

'''绑定设备'''
def binding_device(command):
    if command[-3] == '00':
        return generate_dict_return(1, '绑定成功')
    elif command[-3] == '01':
        return generate_dict_return(0, '绑定失败,系统类型不支持')
    elif command[-3] == '02':
        return generate_dict_return(0, '绑定失败,设备已绑定')

'''绑定设备'''
def unbinding_device(command):
    if command[-3] == '00':
        return generate_dict_return(1, '解除绑定成功')
    elif command[-3] == '01':
        return generate_dict_return(0, '解除绑定失败,参数错误')
    elif command[-3] == '02':
        return generate_dict_return(0, '解除绑定失败,设备未绑定')

'''获取用户配置'''
def get_user_config(command):
    return None

'''检查错误返回解析'''
def check_fail(command):
    resp = {}
    resp["result"] = "fail"
    resp["resultdata"] = {}
    if command[-3] == 'fb':
        resp["resultmessage"] = "不支持的 Command ID"
    elif command[-3] == 'fc':
        resp["resultmessage"] = "不支持的 Key"
    elif command[-3] == 'fd':
        resp["resultmessage"] = " Length 错误"
    elif command[-3] == 'fe':
        resp["resultmessage"] = "Data 错误"
    elif command[-3] == 'ff':
        resp["resultmessage"] = "CRC16 校验错误"

    return resp