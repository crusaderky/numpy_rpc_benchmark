# numpy RPC benchmarks

Performance benchmarks for a RPC server that needs to primarily accept and 
serve large numpy arrays to non-Python clients.
The test servers offer an endpoint that performs a simple 'echo' with a 
numpy payload.

## Benchmarked solutions

### gRPC servers
- grpcio (synchronous, threaded)
- purerpc (async)

### REST servers
- Tornado (synchronous)
- Tornado (async)
- aiohttp (async)

### Message encodings for REST
- JSON; array is converted to a plain python list:
```python
{
  'data': [[1, 2], [3, 4]],
  'dtype': '<i8'
}
```

- JSON; array is converted to base64-encoded bytes:
```python
{
  'buffer': 'AQAAAAAAAAACAAAAAAAAAAMAAAAAAAAABAAAAAAAAAA=',
  'dtype': '<i8',
  'shape': [2, 2]
}
```

- msgpack_numpy:
```python
{
  b'nd': True,
  b'type': b'<i8',
  b'kind': b'',
  b'shape': [2, 2],
  b'data': b'\x01\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00'
           b'\x03\x00\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00'
}

```

## Run benchmark

```shell
git clone https://github.com/crusaderky/numpy_rpc_benchmark
cd numpy_rpc_benchmark-grpc-python
pip install -r requirements.txt
python setup.py build
python server_grpc.py &
python server_purerpc.py &
python server_tornado_sync.py &
python server_tornado_async.py &
python server_aiohttp.py &
python client.py
```

### Results
MacOS High Sierra, Intel Core i7 2.9 GHz

```
######### 1 points (8 bytes), 1000 parallel requests #########
grpc                     :   0.203 ms/request
purerpc                  :   1.691 ms/request
tornado sync msgpack     :   0.760 ms/request
tornado async msgpack    :   0.805 ms/request
asyncio msgpack          :   0.487 ms/request
tornado sync json_binary :   0.723 ms/request
tornado async json_binary:   0.816 ms/request
asyncio json_binary      :   0.516 ms/request
tornado sync json        :   0.720 ms/request
tornado async json       :   0.799 ms/request
asyncio json             :   0.529 ms/request

######### 256 points (2048 bytes), 1000 parallel requests #########
grpc                     :   0.212 ms/request
purerpc                  :   0.828 ms/request
tornado sync msgpack     :   0.726 ms/request
tornado async msgpack    :   0.847 ms/request
asyncio msgpack          :   0.506 ms/request
tornado sync json_binary :   0.766 ms/request
tornado async json_binary:   0.860 ms/request
asyncio json_binary      :   0.525 ms/request
tornado sync json        :   1.213 ms/request
tornado async json       :   1.289 ms/request
asyncio json             :   1.010 ms/request

######### 8192 points (65536 bytes), 1000 parallel requests #########
grpc                     :   0.297 ms/request
purerpc                  :   1.202 ms/request
tornado sync msgpack     :   0.832 ms/request
tornado async msgpack    :   0.965 ms/request
asyncio msgpack          :   0.590 ms/request
tornado sync json_binary :   1.884 ms/request
tornado async json_binary:   2.034 ms/request
asyncio json_binary      :   1.616 ms/request
tornado sync json        :  15.530 ms/request
tornado async json       :  16.116 ms/request
asyncio json             :  15.408 ms/request
```
