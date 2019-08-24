import argparse
import hashlib

import simple_request
ROOT_URL = 'http://10.96.0.6/cgi-bin/'

def get_sha1(value):
    return hashlib.sha1(value.encode()).hexdigest()
    
def get_info():
    # srun get info
    challenge_url = ROOT_URL + 'get_challenge'

def get_encrypted_pw(self,unencrypted_pw):
    md5=hashlib.md5()
    md5.update(unencrypted_pw.encode('utf-8'))
    return md5.hexdigest()
    
class SRUN:
    def __init__(self, username='', password='', region='beijing'):
        self.main_url = ROOT_URL + 'srun_portal'
        password_prefix = '{MD5}'
        self.request_method = 'GET'
        
        self.login_data={'action':'login','username':username,
            'password':password_prefix + self.get_encrypted_pw(password), 'ac_id':'1'}
            
        self.logout_data = {'action':'logout'}    
            
    def login(self):
        f=simple_request.request(self.main_url, request_data=self.login_data)
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
        
    SRUN_Instance=SRUN(args.username, args.password);        
    
    if(args.action == 'logout'):
        SRUN_Instance.logout();
    elif(args.action == 'login'):
        SRUN_Instance.login();
