#! ~/Envs/mfa/flask/bin/python

'''
A proof-of-concept passwordless multi-factor authentications server.
Formerly an orchestra coding challenge.
'''

from flask import Flask, request, abort, jsonify
from random import randrange
import requests
import time
from pprint import pprint
from settings import *

app = Flask(__name__)

@app.route('/auth/request', methods = ['POST'])
def auth_request():
    request_timestamp = int(time.time())
    prelim_request_validation(request.values.keys(), REQUIRED_KEYS_REQUEST)
    check_publickey(request.values['publickey'])
    check_domain(request.values['domain'])
    phone_number = check_name(request.values['name'])
    pin = generate_and_save_pin(request.values['name'], request_timestamp)
    send_pin(phone_number, pin)
    return jsonify( { 'result': 'Success!' } ), 200

@app.route('/auth/check', methods = ['POST'])
def auth_check():
    request_timestamp = int(time.time())
    prelim_request_validation(request.values.keys(), REQUIRED_KEYS_CHECK)
    validate_pin(request.values['name'], request.values['pin'], request_timestamp)
    clean_up_pin_file()
    return jsonify( { 'result': 'Success!' } ), 200

def prelim_request_validation(request_keys, required_keys):
    shared_keys = set(request_keys) & set(required_keys)
    if len(shared_keys) < len(required_keys):
        print("Length of shared keys is wrong: {}".format(len(shared_keys)))
        abort(401)

def check_name(name):
    '''
    Read names and phone numbers from file.
    Return match if found, else abort.
    '''
    with open('names.txt', 'r') as f:
        for line in f:
            line_name, line_phone =  line.split('|')
            if (line_name == name):
                return line_phone
    print("Name {} not found in authorized names.".format(name))
    abort(401)

def check_domain(domain):
    '''
    If domain is found, return, else abort.
    '''
    with open('domains.txt', 'r') as f:
        for line in f:
            if line.strip() == domain:
                return

    print("Domain {} not found in authorized domains.".format(domain))
    abort(401)

def check_publickey(pk):
    '''
    Ensure that public key definition matches sent pk.
    '''
    if pk != PUBLIC_KEY_DEFINITION:
        print("Public Key {} not authorized. Correct key: {}".format(len(pk), len(PUBLIC_KEY_DEFINITION)))
        abort(401)

def send_pin(phone, pin):
    '''
    Call Twilio's sms service.
    TODO: Consider leveraging Twilio API python library
    '''
    url = '{}/Accounts/{}/SMS/Messages.json'.format(TWILIO_BASE_URL,
            TWILIO_ACCOUNT_SID)
    data = {'From': TWILIO_PHONE_NUMBER, 'To': phone, 'Body': pin}
    auth = (TWILIO_ACCOUNT_SID, TWILIO_ACCOUNT_KEY)
    r = requests.post(url, auth=auth, data=data)
    if r.status_code is not 201:
        print("Twilio API request failed with status code {}.".format(r.status_code))
        print("Params: {}.".format(vars(r.request)))
        print("Response: {}.".format(r.text))
        abort(401)


def generate_and_save_pin(name, timestamp):
    '''
    Use randrange to generate an 8-digit length pin.
    Save result in a text file.
    '''
    pin = ''
    for i in range(8):
        val = randrange(10)
        pin += str(val)

    pin_data = '{}|{}|{}\n'.format(name, pin, str(timestamp))

    with open('pins.txt', 'a') as f:
        f.write(pin_data)

    return pin


def validate_pin(name, pin, timestamp):
    valid_lines = []
    with open('pins.txt', 'r') as f:
        for line in reversed(f.readlines()):
            line_name, line_pin, line_timestamp = line.split('|')
            if timestamp > int(line_timestamp) + EXPIRATION_INTERVAL:
                print("Pin is too old.")
                abort(401)
            else:
                if name == line_name and pin == line_pin:
                    return

    print("Pin not found.")
    abort(401)

def clean_up_pin_file():
    '''
    This function would remove all pins
    '''
    pass

if __name__ == '__main__':
    app.run(debug = True)



