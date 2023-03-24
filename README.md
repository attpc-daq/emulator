# emulator
运行两个TCPIP服务器，用于daq程序的测试
IP 0.0.0.0
命令端口8001
数据产生端口8002

例1
通过gui连结emulator，并获取数据。

	1).在emulator运行目录./localfiles/存放准备好的二进制数据文件，每个文件为一个socket数据包。
	2)在gui逐行执行：
		set SiTCP address 0.0.0.0
		set SiTCP port 8002
		run
例2
通过gui发送指令到emulator。

	1)在gui逐行执行：
		set SiTCP address 0.0.0.0
		set SiTCP port 8001
		send_to_SiTCP 12345678
