# Complete project details at https://RandomNerdTutorials.com
#try:
#  import usocket as socket
#except:

import socket
import network
import esp
esp.osdebug(None)
import gc
gc.collect()

ssid = 'MicroPython-AP'
password = '123456789'

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=ssid, password=password)

while ap.active() == False:
  pass

print('Connection successful')
print(ap.ifconfig())


def make_html(data=None):
  head = ['Parameter', 'Value']
 
  html_b = """<!DOCTYPE html>
  <html>
      <head><title>SLCB Modules</title>
      <style>
      table, th, td { border: 1px solid; text-align:left;}
      table { border-collapse: collapse; width:50%; }
      table td:nth-child(2) { text-align: end; }
      </style>
      <meta http-equiv="refresh" content="15"></head>
      <body><h1>SLCB Module Settings</h1>"""

  html_form = '<form action="/" id="choiceform" method="get">' \
              '<label>Choose a command and battery:</label>' \
              '<input type="submit" value="Request"></form>'


  html_e = "</body></html>"

  return html_b + html_form + html_e


def web_page():
  html = """<html><head><meta name="viewport" content="width=device-width, initial-scale=1"></head>
  <body><h1>Hello, World!</h1></body></html>"""
  return html

def safary_page():
  html ="""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <title>Пример HTML для iOS Safari</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f9f9f9;
            color: #333;
        }

        header {
            background-color: #007aff;
            color: white;
            padding: 1rem;
            text-align: center;
        }

        main {
            padding: 1rem;
        }

        .button {
            display: inline-block;
            padding: 0.75rem 1.5rem;
            background-color: #007aff;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: bold;
            text-align: center;
        }

        .button:hover {
            background-color: #005bb5;
        }

        footer {
            text-align: center;
            padding: 1rem;
            background-color: #eaeaea;
            position: fixed;
            bottom: 0;
            width: 100%;
        }
    </style>
</head>
<body>
"""
  return html

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

while True:
  conn, addr = s.accept()
  print('Got a connection from %s' % str(addr))
  request = conn.recv(1024)
  print('Content = %s' % str(request))
  #response = web_page()
  #response = make_html()
  response = safary_page()
  conn.send(response)
  conn.close()
