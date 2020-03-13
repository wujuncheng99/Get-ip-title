#python3
# -*- coding:utf-8 -*-
'''
输入ip段提取该ip开放的端口，有web服务的话提取标题名称
'''
import webbrowser
import socket
import threading
import requests
from bs4 import BeautifulSoup

# 端口扫描
def tcpPortScan(ip, port, openPort):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 创建套接字
    sock.settimeout(1)  # 设置延时时间
    try:
        result = sock.connect_ex((ip, port))
        if result == 0:
            openPort.append(port)  # 如果端口开放，就把端口port赋给openPort
    except:
        pass
    sock.close()

#多线程端口扫描
def threadingPortScan(host, portList, openPorts=[]):
    hostIP = socket.gethostbyname(host)  # 获取域名对应的IP地址
    nloops = range(len(portList))
    threads = []

    for i in nloops:

        t = threading.Thread(target=tcpPortScan, args=(hostIP, portList[i], openPorts))
        threads.append(t)

    for i in nloops:
        threads[i].start()

    for i in nloops:
        threads[i].join()
    openPorts = list(set(openPorts)) #结果发现有重复的port，只能用这个方法了，没发现原因
    return openPorts  # 返回值为该域名下开放的端口列表

#获取网站title
def get_title(url):
    try:
        res = requests.get(url,timeout=5)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'lxml')#解析
        title=soup.title.text
        status_code=res.status_code
        server = res.headers['Server']
    except Exception as e:
        title='无web服务'
        status_code='timeout'
        server=''
    return title, status_code, server




if __name__ == '__main__':
    ip_txt=input('请输入要扫描的ip列表文件：')
    ipfile=open(ip_txt,'r')
    result=open('result.html', 'w')
    html = '''
            <html>
            <head>
            <style> 
            .table-b table,th, td
          {
          font-size:1em;
          border:1px solid #98bf21;
          padding:3px 7px 2px 7px;
          }
          table
          {
          border-collapse:collapse;
          }
        th
          {
          font-size:1.1em;
          text-align:left;
          padding-top:5px;
          padding-bottom:4px;
          background-color:#A7C942;
          color:#ffffff;

          }
            </style>
            <body>
            <div class = "table-b">
            <table border = "0">
                    <tr>
                            <th>URL</th>
                            <th>Status_Code</th>
                            <th>Server</th>
                            <th>Title</th>
                    </tr>'''
    #result.write(html)
    for host in ipfile:
        host=host.strip()
        #host = input('please input domain:')

        #0-10000之间的端口
        portList = range(0, 10000)

        #也可以指定常用端口列表
        #portList=[80,443,1080,1081,8080,8081,8888,9091,9092]
        openPorts = threadingPortScan(host, portList)
        print(host, 'open ports:', openPorts)
        i = 0
        for url in range(len(openPorts)):
            url='http://'+host+':'+str(openPorts[i])
            ip=host+':'+str(openPorts[i])
            i=i+1
            try:
                title,status_code,server=get_title(url)
                print(url)
                print(title)
                print(status_code)

            except Exception as e:
                print(e)


            html += '''
                                                            <tr>
                                                                    <td>%s</td>
                                                                    <td>%s</td>
                                                                    <td>%s</td>
                                                                    <td>%s</td>
                                                            </tr>
                                                            ''' % (ip, status_code, server, title)


    html += '''
             </table>
             </body>
             </html>
             '''
    result.write(html)
    result.close()
    webbrowser.open("result.html", new=1)#自动打开默认浏览器显示结果


