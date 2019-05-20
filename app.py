from aiohttp import web
import paramiko
import threading
import asyncio
import socket
import json
import sys
"""
aiohttp 版本
"""


def command_resize(shell, *, cols, rows):
  """特殊命令, 调整 pty 大小"""
  shell.resize_pty(width=cols, height=rows)


async def run_command(shell, raw_text):
  """处理特殊的命令, 这些命令以 JSON: 开头, 结构为 {"command": "", "kwargs": {}}"""
  try:
    body = json.loads(raw_text[5:])
  except Exception:
    return

  command = body.get('command', '')
  kwargs = body.get('kwargs', {})

  mod = sys.modules[__name__]
  func = getattr(mod, f'command_{command}', None)

  if func:
    func(shell, **kwargs)

  # if command == 'resize':
  #   resize(shell, **kwargs)


async def get_msg(ws, shell):
  """接受消息, 传递给 shell"""
  async for msg in ws:
    print('msg', msg)
    if msg.type == web.WSMsgType.TEXT:

      if msg.data.startswith('JSON:'):
        # 解析特殊的命令, 以 JSON: 开头
        await run_command(shell, msg.data)
      else:
        # 普通的运行, 发送给 shell 处理
        try:
          shell.send(msg.data)
        except asyncio.CancelledError:
          print('CancelledError', 'in get_msg')
        except Exception as e:
          print(type(e), e, 'in get_msg')
    elif msg.type == web.WSMsgType.ERROR:
      return
    elif msg.type == web.WSMsgType.CLOSE:
      return

  print('end get_msg')


async def send_msg(ws, shell, sshclient):
  """从 shell 接受消息, 并发送给前端"""
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


def run_loop_inside_thread(loop):
  loop.run_forever()


def build_ssh(host, port, username, password):
  sshclient = paramiko.SSHClient()
  sshclient.load_system_host_keys()
  sshclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())

  sshclient.connect(host, port, username, password)
  shell = sshclient.invoke_shell(term='xterm')

  return sshclient, shell


class ShellWebsocket(web.View):
  async def get(self):
    host = self.request.query.get('host')
    port = self.request.query.get('port')
    username = self.request.query.get('username')
    password = self.request.query.get('password')

    ws = web.WebSocketResponse()
    available = ws.can_prepare(self.request)
    if not available:
      return web.Response(body='不能建立 websocket 连接')

    await ws.prepare(self.request)

    try:
      sshclient, shell = build_ssh(host, port, username, password)
    except Exception:  # noqa
      await ws.send_str('无法建立 ssh 连接, 请确认用户密码正确')
      await ws.close(message='无法建立 ssh 连接, 请确认用户密码正确')
      return ws

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
