import glob
import re
import shutil
from distutils.command.build_py import build_py
from setuptools import setup, find_packages


class GrpcToolCommand(build_py):
    def run(self):
        super().run()
        import grpc_tools.protoc
        grpc_tools.protoc.main([
            'grpc_tools.protoc',
            '-Iprotos',
            '--python_out=protos',
            '--grpc_python_out=protos',
            '--purerpc_out=protos',
        ] + glob.glob('protos/*.proto'))
        for fname in glob.glob('protos/*_grpc.py'):
            with open(fname) as fh_in, open(fname + '.new', 'w') as fh_out:
                for row in fh_in:
                    row = re.sub(r'^import (.*)_pb2',
                                 r'from . import \1_pb2', row)
                    fh_out.write(row)
            shutil.move(fname + '.new', fname)


setup(
    name='basic-grpc-python',
    cmdclass={
        'build_py': GrpcToolCommand,
    },
    packages=find_packages(exclude=['*_pb2.py', '*_pb2_grpc.py']),
)
