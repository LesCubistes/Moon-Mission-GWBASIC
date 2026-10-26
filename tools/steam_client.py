"""Small local Steam CEF client; no third-party Python dependencies."""
import base64,json,os,socket,struct,urllib.request,urllib.parse

def evaluate(expression,timeout=20):
 targets=json.load(urllib.request.urlopen('http://127.0.0.1:8080/json',timeout=3))
 target=next(t for t in targets if t['title']=='SharedJSContext')
 url=urllib.parse.urlsplit(target['webSocketDebuggerUrl'])
 with socket.create_connection((url.hostname,url.port),timeout=timeout) as s:
  key=base64.b64encode(os.urandom(16)).decode()
  s.sendall(('GET '+url.path+' HTTP/1.1\r\nHost: '+url.netloc+'\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: '+key+'\r\nSec-WebSocket-Version: 13\r\n\r\n').encode())
  header=b''
  while not header.endswith(b'\r\n\r\n'):header+=s.recv(1)
  if b' 101 ' not in header.split(b'\r\n')[0]:raise RuntimeError('Steam CEF handshake failed')
  def send(data,opcode=1):
   mask=os.urandom(4);n=len(data)
   length=bytes([0x80|n]) if n<126 else bytes([0x80|126])+struct.pack('!H',n) if n<65536 else bytes([0x80|127])+struct.pack('!Q',n)
   s.sendall(bytes([0x80|opcode])+length+mask+bytes(c^mask[i%4] for i,c in enumerate(data)))
  def read(n):
   data=b''
   while len(data)<n:
    part=s.recv(n-len(data))
    if not part:raise RuntimeError('Steam CEF disconnected')
    data+=part
   return data
  send(json.dumps({'id':1,'method':'Runtime.evaluate','params':{'expression':expression,'awaitPromise':True,'returnByValue':True}}).encode())
  while True:
   a,b=read(2);n=b&127
   if n==126:n=struct.unpack('!H',read(2))[0]
   elif n==127:n=struct.unpack('!Q',read(8))[0]
   mask=read(4) if b&128 else None;payload=read(n)
   if mask:payload=bytes(c^mask[i%4] for i,c in enumerate(payload))
   if a&15==9:send(payload,10);continue
   if a&15==8:raise RuntimeError('Steam CEF closed the connection')
   if a&15!=1:continue
   message=json.loads(payload)
   if message.get('id')==1:
    if message.get('error') or message.get('result',{}).get('exceptionDetails'):raise RuntimeError('Steam CEF evaluation failed')
    return message['result']['result'].get('value')
