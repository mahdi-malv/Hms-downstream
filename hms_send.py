#!/usr/bin/python3

import argparse
import json
import asyncio
import requests
import configparser
import time


"""
Author : mahdi-malv
Version: 1.0.0
"""

verbose = False
config_name = "hms_config.txt"

def log(message):
    if verbose: print('[Log]:', message)

def cacheToken(token):
    updateConfig('access_token', token)
    updateConfig('access_token_cache_time', time.time())
    log('Access_token cached successfully.')

def readConfig(key, name=config_name):
    c = configparser.ConfigParser()
    c.read(name)
    config = c['DEFAULT']
    if key in config:
        v = config[key]
        if v == '': return False
        else: return v
    else:
        return False

def updateConfig(key, value, name=config_name):
    c = configparser.ConfigParser()
    c.read(name)
    c['DEFAULT'][key] = str(value)
    with open(name, 'w') as file:
        c.write(file)

def getArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--tokens', help='Device tokens', nargs='+')
    parser.add_argument('-d', '--data', help="Pushe data block (courier=pushe will be added auto)", default="{}")
    parser.add_argument('-v', '--verbose', action='store_true', help="See more logs", default=False)
    args = parser.parse_args()


    global verbose
    verbose = args.verbose

    result = {}
    result['tokens'] = args.tokens if args.tokens else []
    if args.tokens:
        result['tokens'] = args.tokens
    elif readConfig('tokens'):
        result['tokens'] = readConfig('tokens').split(',')
    else:
        raise ValueError("tokens must be passed. Either config or --tokens/-t")

    if readConfig('client_id'):
        result['id'] = readConfig('client_id')
    else:
        raise ValueError("client_id must be entered in config file")
    
    if readConfig('client_secret'):
        result['secret'] = readConfig('client_secret')
    else:
        raise ValueError("client_secret must be entered in config file")

    if readConfig('access_token') and readConfig('access_token_cache_time'):
        token = readConfig('access_token')
        if (time.time() - float(readConfig('access_token_cache_time'))) < 3500:
            log('Loaded access_token from cache.')
            result['access_token'] = token
        else:
            log('Cached Access_token is outdated. Clearing...')
            result['access_token'] = ''
            updateConfig('access_token', '')
            updateConfig('access_token_cache_time', '')
    else:
        result['access_token'] = ''


    
    if args.data:
        try:
            data = args.data
        except Exception as e:
            log(f'Failed to parse data: {e}')
            data = {}
        result['data'] = data
    else:
        raise Exception("Must pass -d/--data")

    return result

async def fetchAccessToken(client_id, client_secret):
    url = "https://oauth-login.cloud.huawei.com/oauth2/v2/token"
    log(f'ClientId: {client_id} and secret: {client_secret}')
    payload = f'client_id={client_id}&client_secret={client_secret}&grant_type=client_credentials'
    headers = {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.request("POST", url, headers=headers, data = payload)
    try:
        log(str(response.json()))
        return response.json()['access_token']
    except Exception as e:
        log('Error getting access_token: ' + e)
        return False

async def sendMessage(access_token, data, client_id, tokens):
    url = f"https://push-api.cloud.huawei.com/v1/{client_id}/messages:send"
    message = {
        'message': {
            'message_id': "Message#",
            'token': tokens,
            'data': str(data),
        }
    }
    payload = json.dumps(message)
    log(f'Payload json: {payload}')
    headers = {
      'Authorization': f'Bearer {access_token}',
      'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json()

async def main():
    args = getArguments()
    clientId = args['id']
    clientSecret = args['secret']
    payload = args['data']
    tokens = args['tokens']
    access_token = args['access_token']



    # Access TOKEN
    if(not access_token):
        token = await fetchAccessToken(client_id=clientId, client_secret=clientSecret)
        log('Access_token retrieved from server. Caching...')
        cacheToken(token)
    else:
        token = access_token

    sendResult = await sendMessage(access_token=token, data=payload, client_id=clientId, tokens=tokens)
    print(sendResult)

if __name__ == "__main__":
    asyncio.run(main())
