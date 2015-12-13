import hashlib
import urllib.parse
import urllib.request
import time
import sys

__author__ = 'kees'

HOST = 'http://localhost:8000/'
SECRET = 'UVgxCasmGraXCe2rwU9xCaKDc6mhmhaV7j5Ncpp5KXMhpDsxIVQxsNr9bSjX'


def measure():

    # read lines
    file = open("/sys/bus/w1/devices/28-0000074e073e/w1_slave")
    text = file.read()
    file.close()

    temperature = float(text[-6:])

    post_temperature(temperature/1000)


def post_temperature(temperature):
    """
    run from terminal python3 runner.py measuretemperature to POST temperature to host

    :return:
    """
    url = HOST + 'temperature/'
    values = {'time': int(time.time()),
              'temperature': temperature,
              }
    print('time ' + str(values['time']))
    code = 'time=%s&temperature=%s&secret=%s' % (str(values['time']), str(values['temperature']), SECRET)
    values['hash'] = hashlib.md5(code.encode()).hexdigest()
    print('hash ' + str(values['hash']))
    data = urllib.parse.urlencode(values)
    data = data.encode('ascii')  # data should be bytes
    req = urllib.request.Request(url, data, method='POST')
    with urllib.request.urlopen(req) as response:
        the_page = response.read()
        print(the_page)


if __name__ == "__main__":
    locals()[sys.argv[1]]()
