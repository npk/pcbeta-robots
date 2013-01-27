#!/usr/bin/env python
# -*- coding: gbk -*-

import sys, re, time
import urllib2, cookielib, urllib
import StringIO, gzip, zlib

reload(sys)
sys.setdefaultencoding('gbk')


class UserAgentProcessor(urllib2.BaseHandler):
    
    def http_request(self, request):
        request.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64; rv:10.0.12) Gecko/20100101 Firefox/10.0.12 Iceweasel/10.0.12')
        return request


class EncodingProcessor(urllib2.BaseHandler):
    
    def http_request(self, request):
        request.add_header('Accept-Encoding', 'gzip, deflate')
        return request

    def http_response(self, request, response):
        old_response = response
        if response.headers.get('Content-Encoding') == 'gzip':
            gz = gzip.GzipFile(fileobj=StringIO.StringIO(response.read() ), mode='r')
            response = urllib2.addinfourl(gz, old_response.headers, old_response.url, old_response.code)
            response.msg = old_response.msg
        if response.headers.get('Content-Encoding') == 'deflate':
            gz = StringIO.StringIO(zlib.decompressobj(-zlib.MAX_WBITS).decompress(response.read() ) )
            response = urllib2.addinfourl(gz, old_response.headers, old_response.url, old_response.code)
            response.msg = old_response.msg
        return response


class Pcbeta:
    
    def __init__(self, userinfo):
        self.__username = userinfo['username']
        self.__password = userinfo['password']
        self.__questionid = userinfo['questionid']
        self.__answer = userinfo['answer']
        self.__haslogin = False
        
    def login(self):
        if self.__haslogin == False:
            uap = UserAgentProcessor()
            ep = EncodingProcessor()
            cp = urllib2.HTTPCookieProcessor(cookielib.CookieJar() )
            opener = urllib2.build_opener(uap, ep, cp)
            urllib2.install_opener(opener)
            data = urllib2.urlopen('http://bbs.pcbeta.com/member.php?mod=logging&action=login').read()
            results = re.search(r'id="loginform.+action="([^"]+)', data)
            if results:
                loginpage = results.group(1)
                loginpage = loginpage.replace('&amp;', '&')
            else:
                print 'Error: Could not found login page!'
                sys.exit()
            results = re.search(r'<input type="hidden" name="formhash" value="([^"]+)', data)
            if results:
                formhash = results.group(1)
            else:
                print 'Error: Could not found formhash!'
                sys.exit()
            postdata = urllib.urlencode({
                'formhash': formhash,
                'referer': 'http://bbs.pcbeta.com/forum.php',
                'username': self.__username,
                'password': self.__password,
                'questionid': self.__questionid,
                'answer': self.__answer,
            })
            req = urllib2.Request(
                url = 'http://bbs.pcbeta.com/' + loginpage,
                data = postdata,
            )
            urllib2.urlopen(req)
            data = urllib2.urlopen('http://bbs.pcbeta.com/forum.php').read()
            results = re.search(ur'<a href="http://i.pcbeta.com/space-uid-(\d+).+>([\u0020-\u007e\u4e00-\u9fa5]+)</a>', data.decode('gbk') )
            if results:
                self.__haslogin = True
                self.__uid = results.group(1)
                print u'%s has login success!' % results.group(2)
            else:
                print 'Error: Login failed!'
                sys.exit()
                
    def logout(self):
        if self.__haslogin == True:
            data = urllib2.urlopen('http://bbs.pcbeta.com/forum.php').read()
            results = re.search(r'<input type="hidden" name="formhash" value="([^"]+)', data)
            if results:
                formhash = results.group(1)
            else:
                print 'Error: Could not found formhash!'
                sys.exit()
            urllib2.urlopen('http://bbs.pcbeta.com/member.php?mod=logging&action=logout&formhash='+formhash)
            self.__haslogin == False
            
    def post(self, tid, content):
        if self.__haslogin == True:
            error = False
            data = urllib2.urlopen('http://bbs.pcbeta.com/viewthread-'+tid+'-1-1.html').read()
            results = re.search(r'<form method="post" autocomplete="off" id="fastpostform" action="([^"]+)', data)
            if results:
                postpage = results.group(1)
                postpage = postpage.replace('&amp;', '&')
            else:
                print 'Error: Could not found post page!'
                error = True
            results = re.search(r'<input type="hidden" name="posttime" id="posttime" value="([^"]+)', data)
            if results:
                posttime = results.group(1)
            else:
                print 'Error: Could not found posttime!'
                error = True
            results = re.search(r'<input type="hidden" name="formhash" value="([^"]+)', data)
            if results:
                formhash = results.group(1)
            else:
                print 'Error: Could not found formhash!'
                error = True
            if error == False:
                postdata = urllib.urlencode({
                    'message': content,
                    'posttime': posttime,
                    'formhash': formhash,
                    'subject': '',
                    'usesig': 1
                })
                req = urllib2.Request(
                    url = 'http://bbs.pcbeta.com/' + postpage,
                    data = postdata,
                    headers = {'Referer': 'http://bbs.pcbeta.com/viewthread-'+tid+'-1-1.html'}
                )
                urllib2.urlopen(req)
                
    def passby(self):
        if self.__haslogin == True:
            data = urllib2.urlopen('http://www.pcbeta.com/news/').read()
            results = re.findall(r'<h3><a href="([^"]+)', data)
            if results:
                for n in range(len(results) ):
                    data = urllib2.urlopen(results[n]).read()
                    rdata = re.search(r'<a href="([^"]+)" id="click_aid_\d+_4"', data)
                    if rdata:
                        rdata = rdata.group(1)
                        rdata = rdata.replace('&amp;', '&')
                        urllib2.urlopen(rdata)
                        time.sleep(2)
                        
    def task_qiegao(self):
        if self.__haslogin == True:
            urllib2.urlopen('http://i.pcbeta.com/home.php?mod=task&do=apply&id=53')
            
    def task_xuebangui(self):
        if self.__haslogin == True:
            urllib2.urlopen('http://i.pcbeta.com/home.php?mod=task&do=apply&id=75')
            time.sleep(2)
            self.post('951045', '认认真真学习版规')
            time.sleep(2)
            urllib2.urlopen('http://i.pcbeta.com/home.php?mod=task&do=draw&id=75')
            
            


# questionid为安全问题的编号
#      0 - 未设置安全提问
#      1 - 母亲的名字
#      2 - 爷爷的名字
#      3 - 父亲出生的城市
#      4 - 你其中一位老师的名字
#      5 - 你个人计算机的型号
#      6 - 你最喜欢的餐馆名称
#      7 - 驾驶执照最后四位数字
#  answer为安全问题的答案，如果没有设置安全问题，请留空。

if __name__ == '__main__':
    
    user = {
        'username': 'username',
        'password': 'password',
        'questionid': 0,
        'answer': '',
    }
    
    p = Pcbeta(user)
    p.login()
    p.passby()
    p.task_qiegao()
    p.task_xuebangui()
    p.logout()
