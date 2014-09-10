#!/usr/bin/env python
#coding: utf-8

import psutil
import bottle
from socketio import socketio_manage
from socketio.namespace import BaseNamespace
from socketio.mixins import BroadcastMixin
import gevent
from gevent import monkey

monkey.patch_all()

app = bottle.Bottle()


cpu_count = psutil.cpu_count()

class CPUNamespace(BaseNamespace, BroadcastMixin):
    def recv_connect(self):
        def sendcpu():
            prev = None
            while True:
                vals = psutil.cpu_percent(interval=1, percpu=True)

                if prev:
                    # percent = (sum(vals) - sum(prev))
                    percent = []
                    for i in range(cpu_count):
                        # percent.append(vals[i] - prev[i])
                        percent.append(vals[i])

                    self.emit('cpu_data', {'point': percent})
                prev = vals
                gevent.sleep(0.1)
        self.spawn(sendcpu)



@app.get('/')
def root():
    
    return bottle.template('index.html', cpu_count=cpu_count)



@app.get('/static/<filepath:path>')
def get_static(filepath):
    return bottle.static_file(filepath, root='./static/')
   


@app.get('/socket.io/<path:path>')
def socketio_service(path):
    print 'socketio', path
    socketio_manage(bottle.request.environ,
                    {'/cpu': CPUNamespace}, bottle.request)


if __name__ == '__main__':
    bottle.run(app=app,
               host='127.0.0.1',
               port=8080,
               server='geventSocketIO',
               debug=True,
               reloader=True,
              )
