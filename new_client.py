from help_function import download_chunk_function, setup_socket, download_content_length,get_file_links
import urllib
import io
from sys import stdin
import threading
#from concurrent.futures import ProcessPoolExecutor

def handleConnection(URL):
    #print(len(URL))
    o = urllib.parse.urlsplit(URL)
    BUFSIZE = 1024
    HOST = o.netloc
    socket = setup_socket.create_socket(URL)
    client_type = setup_socket.get_client_type(URL)

    #single main page
    if (client_type == 1):
        request = o.path
        file_name = "index.html"
        stri = f"GET {request} HTTP/1.1\r\nHost: {HOST}\r\n\r\n"
        socket.send(bytes(stri,"utf8"))
        print("For the link " + URL)
        download_option = input("What do you want to use (Content-length/ chunked): ")
        data = b""
        data = socket.recv(BUFSIZE)
        if (download_option == "Content-length"):
            status, headers = download_content_length.dict_headers(io.StringIO(data.decode(encoding="ISO-8859-1")))
            download_content_length.download_content_length(headers,BUFSIZE,data,socket,file_name)
        else:
            download_chunk_function.download_chunked(data,socket,BUFSIZE,file_name)

    #specific file
    if (client_type == 2):
        request = o.path
        tmp, file_name = o.path.rsplit("/", 1)
        stri = f"GET {request} HTTP/1.1\r\nHost: {HOST}\r\n\r\n"
        socket.send(bytes(stri,"utf8"))
        print("For the link " + URL)
        download_option = input("What do you want to use (Content-length/ chunked): ")
        data = b""
        data = socket.recv(BUFSIZE)
        if (download_option == "Content-length"):
            status, headers = download_content_length.dict_headers(io.StringIO(data.decode(encoding="ISO-8859-1")))
            download_content_length.download_content_length(headers,BUFSIZE,data,socket,file_name)
        else:
            download_chunk_function.download_chunked(data,socket,BUFSIZE,file_name)

    #folder

    if (client_type == 3):
        file_links = get_file_links.get_file_links(URL)
        download_content_length.download_folder(file_links,socket,BUFSIZE,HOST)
        
#MainProgram go here
linkSet = set()
for line in stdin:
    lineLength = len(line)
    if (lineLength == 1) : break
    linkSet.add(line)

linkList = list(linkSet)
ListSize = len(linkList)
# for i in range(ListSize):
#     tempLink = linkList[i]
#     linkList[i] = tempLink[:-1]

#Threading
threadList = []
for link in linkList:
    serverThread = threading.Thread(target=handleConnection, args=(link[:-1],))
    threadList.append(serverThread)
    serverThread.start()

[x.join() for x in threadList]


#Processing
# with ProcessPoolExecutor() as exe:
#     exe.map(handleConnection, linkList)