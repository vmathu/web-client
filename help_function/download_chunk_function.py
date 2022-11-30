import io
import os
import urllib

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
    # test = open("testChunked.txt", "wb+")
    for chunk in chunks:
        pos = chunk.find(b"\r\n\r\n")
        if pos != -1:
            chunk = chunk[pos+4:]
        file.write(chunk)
        # test.write(chunk)
    file.close()
    # test.close()
    s.close()


