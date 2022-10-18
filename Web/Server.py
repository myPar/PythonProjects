import sys
from enum import IntEnum
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import mimetypes
import os

PORT = 8080
SERVER = "localhost"

MODE = "mode"
FILE_PATH = "file_path"
modes = ["data", "result"]


class ResponseStatus(IntEnum):
    OK = 200
    BAD_REQUEST = 400
    SERVER_ERROR = 500
    NOT_FOUND = 404


class RequestHandler(BaseHTTPRequestHandler):
    def send_bad_response(self, message:str, status:int):
        print(message, file=sys.stderr)
        self.send_response(code=status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><body><h1>" + message + "</h1></body></html>", "utf-8"))
        self.wfile.flush()

    def send_file_response(self, file, status:int, file_type:str):
        self.send_response(code=status)
        self.send_header("Content-type", file_type)
        self.end_headers()
        self.wfile.write(file.read())
        self.wfile.flush()

    def do_GET(self):
        query = urlparse(self.path).query  # get query from url
        query_components = parse_qs(query)  # get query args

        # get mode value:
        try:
            mode = str(query_components[MODE][0])
        except KeyError:
            self.send_bad_response("No 'mode' parameter found in url", ResponseStatus.BAD_REQUEST)
            return
        # get file_path value:
        try:
            file_path = str(query_components[FILE_PATH][0])
        except KeyError:
            self.send_bad_response("No 'file_path' parameter found in url", ResponseStatus.BAD_REQUEST)
            return
        # check mode value:
        if mode not in modes:
            self.send_bad_response("Invalid mode value - '" + mode + "', use suggested: " + str(modes),
                                   ResponseStatus.BAD_REQUEST)
            return

        if not os.path.isfile(file_path):
            self.send_bad_response("No such file exists: " + file_path, ResponseStatus.NOT_FOUND)
            return

        # get file type:
        file_type = mimetypes.guess_type(file_path)[0]  # returns a tuple (type, encoding)

        if mode == modes[0]:    # send file data
            # open file, read data in binary mode, and send data:
            f = open(file_path, "rb")
            self.send_file_response(file=f, file_type=file_type, status=ResponseStatus.OK)
        elif mode == modes[1]:
            self.send_bad_response("Not supported yet :(", status=ResponseStatus.SERVER_ERROR)
        else:
            assert False


def main():
    server = ThreadingHTTPServer((SERVER, PORT), RequestHandler)
    print("server is running..")
    server.serve_forever()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
