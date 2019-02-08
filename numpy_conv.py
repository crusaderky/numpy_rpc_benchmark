import base64
import numpy
from protos.calculator_pb2 import NDArray


def ndarray_to_message(x: numpy.ndarray) -> NDArray:
    x = numpy.ascontiguousarray(x)
    return NDArray(buffer=x.tobytes(), dtype=x.dtype.str, shape=x.shape)


def message_to_ndarray(x: NDArray) -> numpy.ndarray:
    return numpy.frombuffer(x.buffer, x.dtype).reshape(*x.shape)


def ndarray_to_json(x: numpy.ndarray, binary: bool = True) -> dict:
    if binary:
        return {
            'buffer': base64.b64encode(x.tobytes()).decode('ascii'),
            'dtype': x.dtype.str,
            'shape': list(x.shape)
        }
    return {
        'data': x.tolist(),
        'dtype': x.dtype.str,
    }


def json_to_ndarray(x: dict) -> numpy.ndarray:
    if 'buffer' in x:
        buffer = base64.b64decode(x['buffer'].encode('ascii'))
        return numpy.frombuffer(buffer, x['dtype']).reshape(*x['shape'])
    return numpy.array(x['data'], dtype=x['dtype'])


def json_ndarray_is_binary(x: numpy.ndarray) -> bool:
    return 'buffer' in x
