def download_chunked(data, s, BUFSIZE, file_name):
    chunks = b""
    if data:
        chunks+=data

    while True:
        try:
            data = s.recv(BUFSIZE)
        except OSError:
            break
        else:
            if not data:
                # Client is done with sending.
                break
            chunks+=data

    # Look for the end of the header
    pos = chunks.find(b"\r\n\r\n")

    # Skip past the header and save file data
    file = chunks[pos+4:]
    fwrite = open(file_name, "wb")
    fwrite.write(file)
    fwrite.close()
    s.close()
