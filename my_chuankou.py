import serial # pyserial
import serial.tools.list_ports
import binascii
import time


def uart_output(flag_case,angle=10,portx="COM1",bps=115200,timex=5): #用于发送数据的函数
    #flag_case: 球发给网枪的模式标识，angle：网枪需偏转的角度（竖直为0），portx：端口号，bps：波特率，timex：收发延时

    #对角度进行一个字节长度的映射，目前设置角度左右最大摇摆均为15度
    angle = int((angle+15)*(256/30))
    #将十进制整型角度转化为长度为一个字节的字符型十六进制数（目前未考虑小数和负数）
    if angle <= 16:
        angle_hex = '0'+ hex(angle).replace('0x','') #如果是A-F，则字母全部为小写
    else:
        angle_hex = hex(angle).replace('0x','')
        print("映射后的angle:",angle)
        print("对应的十六进制数:",angle_hex)

    #从串口写数据error
    try:
        # 端口：CNU； Linux上的/dev /ttyUSB0等； windows上的COM3等
        print("正在使用端口：",portx)
    
        # 波特率，标准值有：50,75,110,134,150,200,300,600,1200,1800,2400,4800,9600,19200,38400,57600,115200
        print("当前波特率：",bps)
        # 超时设置，None：永远等待操作；
        #         0：立即返回请求结果；
        #        其他：收发数据前需等待时间（单位为秒）
        #timex默认为5

        # 打开串口，并得到串口对象
        ser = serial.Serial(portx, bps, timeout=timex)
        ser.flushInput() #清空缓冲区

        # 写数据,共四个字节
        # 第一个字节，帧头ox66，第四个字节是校验位，
        # 第二个字节，头两位标识状态，(二进制）00睡眠，11工作，后六位是000000,111101(3D),101100(2C)（分别对应跟随、第一次握手、第三次握手）
        # 第三个字节是角度
        #result = ser.write(chr(0x06).encode("utf-8"))
        if flag_case == 1: #跟随模式
            s = '66C0' + angle_hex #前三个字节
            ver_bin = bin(0x66+0xC0+angle)[-8:] #计算校验位，得到二进制数结果，为了考虑舍去溢出的问题必须得先经过转为二进制的步骤
            ver_hex = hex(int(ver_bin,2)).replace('0x','') #将二进制数结果转为十六进制
            Hex_str = bytes.fromhex(s+ver_hex) #不太懂函数含义，但是配合ser.write使用可以发送数据
            result = ser.write(Hex_str)
            print("显示的四字节数据结果为：",s+ver_hex)
            print("发送的总字节数为：", result)

        elif flag_case == 2: #发射模式，需要进行握手
            #第一次握手
            print("\n开始第一次握手。。。")
            s = '66FD' + angle_hex #前三个字节
            ver_bin = bin(0x66+0xFD+angle)[-8:] #计算校验位，得到低八位的二进制数结果，为了考虑舍去溢出的问题必须得先经过转为二进制的步骤
            ver_hex = hex(int(ver_bin,2)).replace('0x','') #将二进制数结果转为十六进制
            Hex_str = bytes.fromhex(s+ver_hex) #不太懂函数含义，但是配合ser.write使用可以发送数据

            #ver_hex = '66FD80e3'
            #Hex_str = bytes.fromhex(ver_hex)

            result = ser.write(Hex_str)
            print("显示的四字节数据结果为：",s+ver_hex)
            print("发送的总字节数为：", result)
            print("第一次握手完毕")
            #第二次握手，接受数据
                #等待完善。。。
            print("开始第二次握手。。。")
            
            time.sleep(2)
            rec=ser.inWaiting()
            d = ser.read(rec)
            #print(d)
            final_d = str(binascii.b2a_hex(d))[2:4]
            if final_d.upper() == '0B':
                print("第二次握手接收到的信号为：",final_d)  
                print("第二次握手成功")
                # 将接受的16进制数据格式如b'h\x12\x90xV5\x12h\x91\n4737E\xc3\xab\x89hE\xe0\x16'
                #                      转换成b'6812907856351268910a3437333745c3ab896845e016'
                #                      通过[]去除前后的b'',得到我们真正想要的数据
            
                #ser.flushInput() #清空缓冲区
                #第三次握手
                print("开始第三次握手。。。")
                s = '66EC' + angle_hex #前三个字节
                ver_bin = bin(0x66+0xEC+angle)[-8:] #计算校验位，得到低八位的二进制数结果，为了考虑舍去溢出的问题必须得先经过转为二进制的步骤
                ver_hex = hex(int(ver_bin,2)).replace('0x','') #将二进制数结果转为十六进制
                Hex_str = bytes.fromhex(s+ver_hex) #不太懂函数含义，但是配合ser.write使用可以发送数据
                result = ser.write(Hex_str)
                print("显示的四字节数据结果为：",s+ver_hex)
                print("发送的总字节数为：", result)
                print("第三次握手完毕")

                #接收是否发收成功的信号
                
                time.sleep(2)
                rec=ser.inWaiting()
                d = ser.read(rec)
                final_d = str(binascii.b2a_hex(d))[2:4]
                #print("***********************",final_d)  
                if final_d.upper() == '0A':
                    print("\n发射成功")
                else:
                    print("\n已成功发送发射信号，但因为未知原因发射失败")
            else :
                print("第二次握手接收到的信号为：",final_d)  
                print("第二次握手失败，下面重回第一次握手。。。")

        elif flag_case == 0: #睡眠模式，球发给网枪是0x66000066
            Hex_str = bytes.fromhex('66000066') 
            result = ser.write(Hex_str)
            print("显示的四字节数据结果应该为（定值）：'66000066'")
            print("发送的总字节数为：", result)

            time.sleep(2)
            rec=ser.inWaiting()
            d = ser.read(rec)
            #print("d的数据：",d)
            final_d = str(binascii.b2a_hex(d))[2:4]
            print("睡眠模式下，收到的单片机数据：",final_d)
        else:
            print("输入的flag_case有误，不存在该种flag_case！")

        ser.close() # 关闭串口
 
    except Exception as e:
            print("error!", e)        

if __name__ == '__main__':
    #获取可用串口列表
    print("正在获取可用串口列表...")
    port_list = list(serial.tools.list_ports.comports())
    print(port_list)
 
    if len(port_list) == 0:
        print("无可用串口！")
    else:
        for i in range(0, len(port_list)):
            print(port_list[i])
    print("串口列表情况汇报完毕")
    #for i in range(5):
    uart_output(2,portx="COM3")


