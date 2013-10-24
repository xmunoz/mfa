#!/usr/bin/env python

'''
Testing MFA API
'''

import requests
from settings import *

def main():
    request()
    #check()

def request():
    url = 'http://127.0.0.1:5000/auth/request'
    data = {'name': 'cristina', 'domain': 'something.com', 'publickey': PUBLIC_KEY_DEFINITION}
    r = requests.post(url,  data=data)
    print r.status_code

def check():
    url = 'http://127.0.0.1:5000/auth/check'
    data = {'name': 'cristina', 'domain': 'something.com', 'pin': '63052470'}
    r = requests.post(url,  data=data)
    print r.status_code

if __name__ == '__main__':
    main()
