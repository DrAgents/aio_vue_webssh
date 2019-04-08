from aiohttp import web
import paramiko
import threading
import asyncio
import socket


"""
aiohttp 版本
"""


async def send_msg(ws, shell, sshclient):
  shell.settimeout(1)
  while not ws.closed:
    await asyncio.sleep(0.1)
    try:
      data = shell.recv(1024)
      print(data)
      await ws.send_bytes(data)
    except socket.timeout:
      pass
    except Exception as e:
      print(e)

  sshclient.close()
  print('end send_msg')
  return False


async def get_msg(ws, shell):
  async for msg in ws:
    print('msg', msg)
    try:
      shell.send(msg.data)
    except Exception as e:
      print(e)

  print('end get_msg')


def run_loop_inside_thread(loop):
  loop.run_forever()


class ShellWebsocket(web.View):
  async def get(self):
    host = self.request.query.get('host')
    port = self.request.query.get('port')
    username = self.request.query.get('username')
    password = self.request.query.get('password')

    ws = web.WebSocketResponse()
    sshclient = paramiko.SSHClient()
    sshclient.load_system_host_keys()
    sshclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
      sshclient.connect(host, port, username, password)
    except Exception as e:  # noqa
      ws.send_str('无法建立连接, 请确认用户密码正确')
      return

    shell = sshclient.invoke_shell(term='xterm')

    await ws.prepare(self.request)

    loop = asyncio.new_event_loop()
    t = threading.Thread(target=run_loop_inside_thread, args=(loop, ))
    t.start()

    asyncio.run_coroutine_threadsafe(send_msg(ws, shell, sshclient), loop)

    await get_msg(ws, shell)
    print('websocket connection closed')

    loop.stop()

    return ws


app = web.Application()
app.add_routes([web.view('/terminals/', ShellWebsocket)])

web.run_app(app, port=3000)
