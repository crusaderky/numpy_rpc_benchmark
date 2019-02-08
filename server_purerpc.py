from purerpc import Server
from numpy_conv import ndarray_to_message, message_to_ndarray
from protos.calculator_grpc import CalculatorServicer


class Calculator(CalculatorServicer):
    async def Echo(self, message):
        a = message_to_ndarray(message)
        return ndarray_to_message(a)


server = Server(50052)
server.add_service(Calculator().service)
server.serve()
