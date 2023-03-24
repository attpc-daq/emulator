# -*- coding:utf-8 -*-

from sitcpy.rbcp_server import PseudoDevice

def main(args=None):
    command_port=8001
    data_port=8002
    PseudoDevice(command_port,data_port).run_loop()

if __name__ == "__main__":
    main()
