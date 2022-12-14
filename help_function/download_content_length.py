import os
import io
import urllib

# get header for content-length


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


# Content-length
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
    s.close()

# Content-length but for folder


def download_content_length_folder(headers, BUFSIZE, data, s, path):
    if "Content-Length" in headers:
        l_content = int(headers['Content-Length'])
    else:
        l_content = len(data)
    file = b""
    if data:
        file = data
        l_content -= len(data)

    while (l_content > 0):
        data = s.recv(min(l_content, BUFSIZE))
        l_content -= len(data)
        file += data

    # Look for the end of the header
    pos = file.find(b"\r\n\r\n")

    # Skip past the header and save file data
    file = file[pos+4:]
    fwrite = open(path, "wb+")
    fwrite.write(file)
    fwrite.close()

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

        s.sendall(bytes(stri, "utf-8"))
        data = s.recv(BUFSIZE)
        status, headers = dict_headers(
            io.StringIO(data.decode(encoding="ISO-8859-1")))
        download_content_length_folder(headers, BUFSIZE, data, s, path)

    s.close()
