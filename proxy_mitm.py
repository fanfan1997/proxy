#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from flask_script import Command
from mitmproxy import flow, controller, options
from mitmproxy.proxy import ProxyServer, ProxyConfig
import datetime
from setting import *
import pymysql
import sys
reload(sys)
sys.setdefaultencoding('utf8')


con = pymysql.connect(host=HOST, user=USER,password=PASSWORD,port=PORT,db =DB)
cur = con.cursor()


class MyMaster(flow.FlowMaster):

    def run(self):
        try:
            flow.FlowMaster.run(self)
        except KeyboardInterrupt:

            self.shutdown()

    @controller.handler
    def request(self, f):
      try:
        print("request", vars(f))
        print f.request.headers
        print f.request.cookies.to_dict()
        nowtime = datetime.datetime.now()
        now = nowtime.strftime('%Y-%m-%d %H:%M:%S')
        detaday = datetime.timedelta(minutes=30)
        da_days = nowtime + detaday
        m_date = da_days.strftime('%Y-%m-%d %H:%M:%S')
        print '----------------------------------'
        print str(f.request.cookies.to_dict()['JSESSIONID'])
        cur.execute('INSERT IGNORE INTO session_id(`session`, `create_date`,`expire`)  VALUES ("%s", "%s", "%s")'%
                            (str(f.request.cookies.to_dict()['JSESSIONID']),now, m_date ))

        con.commit()
      except :
          pass

    @controller.handler
    def response(self, f):
        try:
            nowtime = datetime.datetime.now()
            now = nowtime.strftime('%Y-%m-%d %H:%M:%S')
            detaday = datetime.timedelta(minutes=30)
            da_days = nowtime + detaday
            m_date = da_days.strftime('%Y-%m-%d %H:%M:%S')
            path_url = f.request.path  # 链接地址
            user_agent = f.request.headers.to_dict()  # headers
            cookie = f.request.cookies.to_dict()  # Cookie
            print path_url
            print '---------------------------------------------------'
            print 'response(session): ', str(json.loads(json.dumps(cookie))['JSESSIONID'])
            cur.execute('INSERT IGNORE INTO session_id(`session`, `create_date`,`expire`)  VALUES ("%s", "%s", "%s")'%(str(json.loads(json.dumps(cookie))['JSESSIONID']),now, m_date))
            con.commit()
        except :
            pass

class Agency(Command):
    def run(self, port):
        if not port:
            port = 38080
        else:
            port = int(port)
        opts = options.Options(
            listen_port=port,
            ssl_insecure=True,
        cadir='mitm_proxy/.mitmproxy')
        config = ProxyConfig(opts)
        state = flow.State()
        server = ProxyServer(config)
        m = MyMaster(opts, server, state)
        m.run()

if __name__ == '__main__':
     print 'start'
     Agency().run(PROXY_PORT)