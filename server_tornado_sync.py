import json
import msgpack
import msgpack_numpy
from tornado.web import Application, RequestHandler
from tornado.ioloop import IOLoop
from numpy_conv import json_to_ndarray, ndarray_to_json, json_ndarray_is_binary


msgpack_numpy.patch()


class EchoJSONHandler(RequestHandler):
    def post(self):
        data = json.loads(self.request.body)
        a = json_to_ndarray(data)
        self.write(ndarray_to_json(a, binary=json_ndarray_is_binary(data)))


class EchoMSGPackHandler(RequestHandler):
    def post(self):
        a = msgpack.unpackb(self.request.body, raw=True)
        self.write(msgpack.packb(a, use_bin_type=True))


urls = [
    ("/echo_json", EchoJSONHandler),
    ("/echo_msgpack", EchoMSGPackHandler),
]
app = Application(urls)
app.listen(50053)
IOLoop.instance().start()
