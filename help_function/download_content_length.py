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
            if l_content < 0:
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


def download_content_length_folder(headers, BUFSIZE, data, s, path, l_header):
    if "Content-Length" in headers:
        l_content = int(headers['Content-Length']) + l_header
    else:
        l_content = len(data) + l_header
    file = b""
    if data:
        file += data
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
    for link in links:
        dir = os.path.join(os.getcwd(), link.split('/')[-2])
        if not os.path.exists(dir):
            os.mkdir(dir)
        file_name = link.split('/')[-1]
        path = os.path.join(dir, file_name)

        stri = f"GET {urllib.parse.urlsplit(link).path} HTTP/1.1\r\nHost: {HOST}\r\nConnection: keep-alive\r\n\r\n"

        s.sendall(bytes(stri, "utf-8"))
        data = s.recv(BUFSIZE)
        pos = data.find(b"\r\n\r\n")
        tmp_data = data[:pos+4]
        l_header = len(tmp_data)
        status, headers = dict_headers(
            io.StringIO(data.decode(encoding="ISO-8859-1")))
        download_content_length_folder(
            headers, BUFSIZE, data, s, path, l_header)

    s.close()
