# -*- coding:utf-8 -*-
import argparse
from sitcpy.rbcp_server import DataGenerator, SessionThreadGen
from sitcpy.cui import CuiServer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', default=8001)
    args = parser.parse_args()

    handler = DataGenerator()
    server = CuiServer(SessionThreadGen, handler, args.port)
    server.start()

if __name__ == "__main__":
    main()
