import argparse
import hashlib
import re
import os
import simple_request
import hmac
import time
from srun_base64 import get_base64
from srun_xencode import get_xencode

from pathlib import Path

ROOT_URL = 'invalid'
n = '200'
type = '1'
ac_id='1'
enc = "srun_bx1"

def get_root_url_inner():
    res = simple_request.request('http://www.baidu.com')
    st = res.url
    if(st.find('baidu') > 0):
        return 'online'
    else:
        url_ip = re.search('http://(.*?)/srun', st).group(1)
        return url_ip

def get_root_url():
    global ROOT_URL
    home = str(Path.home())
    config_file = os.path.join(home, '.srun.config')
    if(os.path.exists(config_file)):
        with open(config_file) as f:
            ROOT_URL = 'http://' + f.read() + '/cgi-bin/'
    else:
        url_ip = get_root_url_inner()
        if(url_ip == 'online'):
            raise ValueError("For the first use, please logout first")
        elif(url_ip == ''):
            raise ValueError("Automatic configuration of authentication ip failed, please write the ip to " + config_file)
        with open(config_file, 'w') as f:
            f.write(url_ip)
        ROOT_URL = 'http://' + url_ip + '/cgi-bin/'
        
def get_md5(password,token):
	return hmac.new(token.encode(), password.encode(), hashlib.md5).hexdigest()
    
def get_sha1(value):
    return hashlib.sha1(value.encode()).hexdigest()
    
def get_token(username, ip):
    # srun get info
    challenge_url = ROOT_URL + 'get_challenge'
    params = {
        "callback": "jQuery112404953340710317169_"+str(int(time.time()*1000)),
        "username":username,
        "ip":ip,
        "_":int(time.time()*1000),
    }
    get_challenge_res = simple_request.request(challenge_url, request_data=params)
    token = re.search('"challenge":"(.*?)"',get_challenge_res.read().decode('utf-8')).group(1)    
    return token

def get_chksum(token, hmd5, username, password, ip, i):
    chkstr = token+username
    chkstr += token+hmd5
    chkstr += token+ac_id
    chkstr += token+ip
    chkstr += token+n
    chkstr += token+type
    chkstr += token+i
    return get_sha1(chkstr)
    
def init_getip():
    init_res = simple_request.request(ROOT_URL)
    ip = re.search('id="user_ip" value="(.*?)"',init_res.read().decode('utf-8')).group(1)
    return ip
    
def get_info(username, password, ip, token):
    info_temp={
        "username":username,
        "password":password,
        "ip":ip,
        "acid":ac_id,
        "enc_ver":enc
    }
    i=re.sub("'",'"',str(info_temp))
    i=re.sub(" ",'',i)
    return "{SRBX1}" + get_base64(get_xencode(i,token))
    
    
class SRUN:
    def __init__(self, username='', password='', region='beijing'):
        self.main_url = ROOT_URL + 'srun_portal'
        password_prefix = '{MD5}'
        self.request_method = 'GET'                            
        self.logout_data = {'action':'logout'}            
        self.username = username
        self.password = password
    def login(self):    
        ip = init_getip()    
        token = get_token(self.username, ip)
        hmd5 = get_md5(self.password, token)
        i = get_info(self.username, self.password, ip, token)
        chksum = get_chksum(token, hmd5, self.username, self.password, ip, i)
        srun_portal_params={
            'callback': 'jQuery11240645308969735664_'+str(int(time.time()*1000)),
            'action':'login',
            'username':self.username,
            'password':'{MD5}' + hmd5,
            'ac_id':ac_id,
            'ip':ip,
            'chksum':chksum,
            'info':i,
            'n':n,
            'type':type,
            'os':'windows+10',
            'name':'windows',
            'double_stack':'0',
            '_':int(time.time()*1000)
            }        
        f=simple_request.request(self.main_url, request_data=srun_portal_params)
        print(f.read().decode('utf-8'))
        
    def logout(self):
        f=simple_request.request(self.main_url, request_data=self.logout_data)
        print(f.read().decode('utf-8'))



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', default=False, type=bool, nargs='?', const=True, help='whether to enter debug mode') 
    parser.add_argument('action', default='login', choices=['login','logout'])
    parser.add_argument('username', default='abc', nargs='?')
    parser.add_argument('password', default='123', nargs='?')
    
    args = parser.parse_args()
    
    if(args.debug):
        import pdb
        pdb.set_trace()
        
    get_root_url()    
    SRUN_Instance=SRUN(args.username, args.password);        
    
    if(args.action == 'logout'):
        SRUN_Instance.logout();
    elif(args.action == 'login'):
        SRUN_Instance.login();
