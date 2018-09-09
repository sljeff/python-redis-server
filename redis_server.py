from socketserver import TCPServer, StreamRequestHandler
from resp import handle_line


class RedisHandler(StreamRequestHandler):
    def handle(self):
        state = None
        while True:
            data = self.rfile.readline().strip()
            print(data)
            state = handle_line(data, state)
            if state.is_stoped:
                break
        self.wfile.write(b'+OK\r\n')
        print('end')


if __name__ == '__main__':
    host, port = 'localhost', 6379
    with TCPServer((host, port), RedisHandler) as server:
        server.serve_forever()
