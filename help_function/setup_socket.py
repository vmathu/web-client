import socket
import urllib.parse

def create_socket(URL):
    #print(URL)
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    o = urllib.parse.urlsplit(URL)
    HOST = o.netloc
    PORT = 80
    ADDR = (HOST,PORT)
    s.connect(ADDR)
    return s

def get_client_type(URL):
    if (URL.count('/') == 3) and (URL[-1] == '/'): return 1
    if (URL.count('/') >= 3) and (URL[-1] != '/'): return 2
    if (URL.count('/') >= 3) and (URL[-1] == '/'): return 3
    