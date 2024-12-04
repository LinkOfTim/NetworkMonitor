import socket
import fcntl
import struct
import array

def get_network_interfaces():
    """
    Возвращает список доступных сетевых интерфейсов.
    """
    max_possible = 128  # Максимальное количество интерфейсов
    bytes = max_possible * 32
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    names = array.array('B', b'\0' * bytes)
    outbytes = struct.unpack('iL', fcntl.ioctl(
        s.fileno(),
        0x8912,  # SIOCGIFCONF
        struct.pack('iL', bytes, names.buffer_info()[0])
    ))[0]
    namestr = names.tobytes()
    interfaces = []
    for i in range(0, outbytes, 40):
        name = namestr[i:i+16].split(b'\0', 1)[0]
        interfaces.append(name.decode('utf-8'))
    return interfaces
