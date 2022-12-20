import struct
import crcmod


def crc_16(command):
    # select Crc16CcittFalse
    crc16 = crcmod.mkCrcFun(0x11021, 0xFFFF, False, 0x0000)
    # calc
    crc = crc16(command)
    crc = "%04x" % (struct.unpack(">H", struct.pack("<H", crc))[0])
    #    print(crc)
    return crc

