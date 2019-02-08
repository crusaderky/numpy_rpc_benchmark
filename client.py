import time
import aiohttp
import asyncio
import grpc
import msgpack
import msgpack_numpy
import numpy

from protos.calculator_pb2_grpc import CalculatorStub
from numpy_conv import (ndarray_to_json, json_to_ndarray,
                        message_to_ndarray, ndarray_to_message)

msgpack_numpy.patch()


COUNT = 1000
SIZE = 1024


def bench_grpc(host, size=SIZE, count=COUNT):
    channel = grpc.insecure_channel(host)
    stub = CalculatorStub(channel)
    a = numpy.random.rand(int(size / 8))
    t0 = time.time()

    futures = [
        stub.Echo.future(ndarray_to_message(a))
        for _ in range(count)
    ]
    for future in futures:
        b = message_to_ndarray(future.result())

    t1 = time.time()
    numpy.testing.assert_array_equal(a, b)
    return (t1 - t0) / count * 1000


async def echo_rest(session, host, a, fmt='msgpack'):
    if fmt == 'msgpack':
        url = f'http://{host}/echo_msgpack'
        data = msgpack.packb(a, use_bin_type=True)
        async with session.post(url, data=data) as response:
            return msgpack.unpackb(await response.read(), raw=True)

    elif fmt in {'json', 'json_binary'}:
        url = f'http://{host}/echo_json'
        data = ndarray_to_json(a, binary=fmt.endswith('binary'))
        async with session.post(url, json=data) as response:
            return json_to_ndarray(await response.json())
    else:
        assert False


async def loop_echo_rest(host, a, fmt='msgpack'):
    async with aiohttp.ClientSession() as session:
        finished, unfinished = await asyncio.wait([
            echo_rest(session, host, a, fmt=fmt)
            for _ in range(COUNT)
        ], return_when=asyncio.FIRST_COMPLETED)
        if unfinished:
            await asyncio.wait(unfinished)
    b = await finished.pop()
    return b


def bench_rest(host, size=SIZE, count=COUNT, fmt='msgpack'):
    a = numpy.random.rand(int(size / 8))
    loop = asyncio.get_event_loop()
    t0 = time.time()

    b = loop.run_until_complete(loop_echo_rest(host, a, fmt=fmt))

    t1 = time.time()
    numpy.testing.assert_array_equal(a, b)
    return (t1 - t0) / count * 1000


def main():
    for size in (8, 2048, 65536):
        print(f'######### {size//8} points ({size} bytes), '
              f'{COUNT} parallel requests #########')
        for server_label, port in (
                ('grpc', 50051),
                ('purerpc', 50052)):
            t = bench_grpc(f'localhost:{port}', size=size)
            print(f'{server_label:25}: {t:7.3f} ms/request')

        for fmt in ('msgpack', 'json_binary', 'json'):
            for server_label, port in (
                    ('tornado sync', 50053),
                    ('tornado async', 50054),
                    ('asyncio', 50055)):
                t = bench_rest(f'localhost:{port}', fmt=fmt, size=size)
                label = f'{server_label} {fmt}'
                print(f'{label:25}: {t:7.3f} ms/request')
        print()


if __name__ == '__main__':
    main()
