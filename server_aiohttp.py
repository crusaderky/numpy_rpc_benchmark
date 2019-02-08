import msgpack
import msgpack_numpy
from aiohttp import web
from numpy_conv import json_to_ndarray, ndarray_to_json, json_ndarray_is_binary

msgpack_numpy.patch()
routes = web.RouteTableDef()


@routes.post('/echo_json')
async def echo_json(request: web.Request) -> web.Response:
    data = await request.json()
    a = json_to_ndarray(data)
    return web.json_response(
        ndarray_to_json(a, binary=json_ndarray_is_binary(data)))


async def unpack(request: web.Request):
    return msgpack.unpackb(await request.read(), raw=True)


def pack(response) -> web.Response:
    return web.Response(body=msgpack.packb(response, use_bin_type=True),
                        content_type='application/x-msgpack')


@routes.post('/echo_msgpack')
async def echo_msgpack(request: web.Request) -> web.Response:
    a = await unpack(request)
    return pack(a)


app = web.Application()
app.add_routes(routes)
web.run_app(app, port=50055)
