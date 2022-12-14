import socket
import io
import urllib.parse
import requests
import os
from bs4 import BeautifulSoup
import threading


def dict_headers(ioheaders: io.StringIO):
    status = ioheaders.readline().strip()
    headers = {}
    for line in ioheaders:
        item = line.strip()
        if not item:
            break
        item = item.split(':', 1)
        if len(item) == 2:
            key, value = item
            headers[key] = value
    return status, headers

# Download type Content-length


def download_content_length(headers, BUFSIZE, data, s, file_name):
    if "Content-Length" in headers:
        l_content = int(headers['Content-Length'])
    else:
        l_content = len(data)
    file = b""
    if data:
        file = data
        l_content -= len(data)

    while True:
        try:
            data = s.recv(BUFSIZE)
            l_content -= len(data)
        except OSError:
            break
        else:
            file += data
            if l_content <= 0:
                break

    # Look for the end of the header
    pos = file.find(b"\r\n\r\n")

    # Skip past the header and save file data
    file = file[pos+4:]
    fwrite = open(file_name, "wb+")
    fwrite.write(file)
    fwrite.close()


# Download type Transfer-Encoding: chunked


def download_chunked(data, s, BUFSIZE, file_name):
    chunks = []
    if data:
        chunks.append(data)

    while True:
        try:
            data = s.recv(BUFSIZE)
        except OSError:
            break
        else:
            if not data:
                # Client is done with sending.
                break
            chunks.append(data)

    # s.sendall(b''.join(chunks))

    file = open(file_name, "wb")
    for chunk in chunks:
        pos = chunk.find(b"\r\n\r\n")
        if pos != -1:
            chunk = chunk[pos+4:]
        file.write(chunk)
    file.close()


def get_file_links(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    links = soup.find_all("a")
    file_links = [url+link['href']
                  for link in links if link['href'].endswith('pdf')]
    return file_links


def myclient(ip, port, msg, file_name, bufsize):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    sock.sendall(bytes(msg, "utf-8"))
    result = sock.recv(bufsize)
    if result:
        download_chunked(result, sock, 1024, file_name)
    sock.close()


# Download folder
def download_folder(links, s, BUFSIZE, HOST):
    thread_list = []
    for link in links:
        dir = os.path.join(os.getcwd(), link.split('/')[-2])
        if not os.path.exists(dir):
            os.mkdir(dir)
        file_name = link.split('/')[-1]
        path = os.path.join(dir, file_name)

        stri = f"GET {urllib.parse.urlsplit(link).path} HTTP/1.1\r\nHost: {HOST}\r\n\r\n"

        client_thread = threading.Thread(target=myclient, args=(HOST, 80, stri, path, BUFSIZE))
        thread_list.append(client_thread)
        client_thread.start()

        # s.sendall(bytes(stri, "utf-8"))
        # data = s.recv(BUFSIZE)
        # if data:
        #     download_chunked(data, s, BUFSIZE, path)

    [x.join() for x in thread_list]


# Main


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

URL = input("Enter URL: ")
o = urllib.parse.urlsplit(URL)
HOST = o.netloc
PORT = 80

BUFSIZE = 1024

s.connect((HOST, PORT))


file_name = ""
DOWNLOAD_TYPE = ""
if o.path != "":
    request = o.path
    if o.path != "/":
        tmp, file_name = o.path.rsplit("/", 1)
        if file_name == "":
            DOWNLOAD_TYPE = "Folder"
else:
    request = URL
if file_name == "":
    file_name = "index.html"

if DOWNLOAD_TYPE == "":
    stri = f"GET {request} HTTP/1.1\r\nHost: {HOST}\r\n\r\n"
    s.send(bytes(stri, "utf8"))

    data=b""
    data = s.recv(BUFSIZE)

    if data:
        status, headers = dict_headers(
            io.StringIO(data.decode(encoding="ISO-8859-1")))
        if status == "HTTP/1.1 200 OK":
            DOWNLOAD_TYPE = input(
                "Enter download type (Content-length/ Chunked): ")

            if DOWNLOAD_TYPE == "Content-length":
                download_content_length(headers, BUFSIZE, data, s, file_name)
            else:
                download_chunked(data, s, BUFSIZE, file_name)
        else:
            print(status)
else:
    file_links = get_file_links(URL)
    download_folder(file_links, s, BUFSIZE, HOST)

s.close()