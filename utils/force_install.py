import os
import subprocess
import sys
# 有些包不太好下，可以用这个脚本清除代理后代理清华镜像下载
# 1. 强行在当前 Python 进程中抹除所有可能引起异常的代理变量
proxy_keys = ['http_proxy', 'https_proxy', 'all_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY']
for key in proxy_keys:
    if key in os.environ:
        print(f"[*] 发现并清除本地环境干扰变量: {key} = {os.environ[key]}")
        del os.environ[key]

# 2. 组装 pip 安装命令，强制清空代理参数，并使用国内镜像
command = [
    sys.executable, "-m", "pip", "install",
    "langchain-text-splitters",
    "-i", "https://pypi.tuna.tsinghua.edu.cn/simple",
    "--proxy", ""
]

print("\n[*] 开始在纯净隔离环境下执行安装...")
result = subprocess.run(command)

if result.returncode == 0:
    print("\n[+] 安装成功！")
else:
    print(f"\n[-] 安装失败，退出码: {result.returncode}")