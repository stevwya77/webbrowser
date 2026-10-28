import socket
import ssl
from pathlib import Path

class URL:
    def __init__(self, url):
        ''' Parse scheme '''
        try:
            self.scheme, url = url.split("://", 1)
        except:
            self.scheme = None
            self.path = url

        if self.scheme == "file":
            self.path = url
            self.file_mode = "file"
        elif self.scheme in ["http", "https"]:
            self.file_mode = "web"
            
            if self.scheme == "http":
                self.port = 80
            if self.scheme == "https":
                self.port = 443
            
            if '/' not in url:
                url = url + '/'
            
            '''Parse host & path'''
            self.host, url = url.split('/', 1)
            if ':' in self.host:    #  custom port
                self.host, port = self.host.split(':', 1)
                self.port = int(port)
            self.path = '/' + url
        else:
            self.file_mode = "idle"


    '''
    Request to other server
    '''
    def request(self):
        if self.file_mode == "idle":
            return "", self.file_mode
        if self.file_mode == "file":
            return self.path, self.file_mode
        s = socket.socket(
            family=socket.AF_INET,    #  how to find other computer
            type=socket.SOCK_STREAM,    #  send arbitray amnts data
            proto=socket.IPPROTO_TCP,    #  steps to establish connection (protocol)
        )
        s.connect((self.host, self.port))
        if self.scheme == "https":    #  wrap socket with ssl lib
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)

        request = "GET {} HTTP/1.1\r\n".format(self.path)    #  method, version, path
        request += "Host: {}\r\n".format(self.host)    #  header, value
        request += "User-Agent: {} LilJankyBroswer/.1\r\n"
        request += "Connection: {} close\r\n"
        request += "\r\n"    #  request separation
        s.send(request.encode("utf8"))    #  bytes to str

        response = s.makefile("r", encoding="utf8", newline="\r\n")    #  return object of bytes received from server
        statusline = response.readline()    #  split statusline first
        version, status, explanation = statusline.split(" ", 2)

        response_headers = {}
        while True:
            line = response.readline()
            if line == "\r\n": break
            header, value = line.split(':', 1)    #  split headers
            response_headers[header.casefold()] = value.strip()
            assert "transfer-encoding" not in response_headers
            assert "content-encoding" not in response_headers

        content = response.read()    #  body to be displayed
        s.close()
        return content, self.file_mode

'''
Print text of HTML without tags
'''
def show(body):
    in_tag = False
    for c in body:
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            print(c, end="")

'''
Load web page
'''
def load(url):
    body, type = url.request()
    if type == "idle":
        body = Path("home.txt").read_text(encoding="utf-8")
    if type == "file":
        body = Path(body).read_text(encoding="utf-8")
    show(body)

if __name__ == "__main__":
    import sys
    try:
        load(URL(sys.argv[1]))
    except:
        load(URL(""))