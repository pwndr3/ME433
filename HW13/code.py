import os
import time
import ipaddress
import wifi
import socketpool
import board
import microcontroller
import terminalio
from digitalio import DigitalInOut, Direction
from adafruit_datetime import datetime
from adafruit_httpserver.server import HTTPServer
from adafruit_httpserver.request import HTTPRequest
from adafruit_httpserver.response import HTTPResponse
from adafruit_httpserver.methods import HTTPMethod
from adafruit_httpserver.mime_type import MIMEType

#  onboard LED setup
led = DigitalInOut(board.LED)
led.direction = Direction.OUTPUT
led.value = False

#  connect to network
print("Connecting to WiFi")

#  connect to your SSID
wifi.radio.connect(os.getenv('CIRCUITPY_WIFI_SSID'), os.getenv('CIRCUITPY_WIFI_PASSWORD'))

print("Connected to WiFi")
pool = socketpool.SocketPool(wifi.radio)
server = HTTPServer(pool, "/static")

# variables for HTML
unit = "C"
#  font for HTML
font_family = "monospace"
last_clicked = datetime.now()

#  the HTML script
#  setup as an f string
#  this way, can insert string variables from code.py directly
#  of note, use {{ and }} if something from html *actually* needs to be in brackets
#  i.e. CSS style formatting
def webpage():
    temp = str(microcontroller.cpu.temperature)

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta http-equiv="Content-type" content="text/html;charset=utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.4/jquery.min.js"></script>
    <style>
    html{{font-family: {font_family}; background-color: lightgrey;
    display:inline-block; margin: 0px auto; text-align: center;}}
      h1{{color: deeppink; width: 200; word-wrap: break-word; padding: 2vh; font-size: 20px;}}
      p{{font-size: 15px; width: 200; word-wrap: break-word;}}
      .button{{font-family: {font_family};display: inline-block;
      background-color: black; border: none;
      border-radius: 4px; color: white; padding: 5px 5px;
      text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}}
      p.dotted {{margin: auto;
      width: 75%; font-size: 15px; text-align: center;}}
    </style>
    </head>
    <body>
    <title>Pico W HTTP Server</title>
    <h1>Pico W HTTP Server</h1>
    <br>
    <p class="dotted">This is a Pico W running an HTTP server with CircuitPython.</p>
    <br>
    <p class="dotted">The current ambient temperature near the Pico W is
    <span style="color: deeppink;"><span id="temp">{temp}</span>°C</span></p><br>
    <h1>Control the LED on the Pico W with these buttons:</h1><br>
    <p><button class="button LED-btn" name="LED" value="ON" type="submit">LED ON</button></a></p>
    <p><button class="button LED-btn" name="LED" value="OFF" type="submit">LED OFF</button></a></p><br/>
    <p><button class="button" id="stopwatch-btn" name="stopwatch" type="submit">Stopwatch</button></a></p>
    <p>Time from last click: <span id="stopwatch-time">0:00:00</span>
    </body>
    <script>
    // LED buttons handler
    $(".LED-btn").click((el) => {{ $.post("/led", {{[el.target.name]: el.target.value}}) }});
    // Stopwatch button handler
    $("#stopwatch-btn").click((el) => {{
        $.get("/stopwatch", (data) => {{
            $("#stopwatch-time").text(data);
        }});
    }});
    // 1 sec temperature refresher
    setInterval(() => {{
        $.get("/temp", (data) => {{
            $("#temp").text(data);
        }});
    }}, 1000);
    </script>
    </html>
    """
    return html

#  route default static IP
@server.route("/")
def base(request: HTTPRequest):
    #  serve the HTML f string
    #  with content type text/html
    with HTTPResponse(request, content_type=MIMEType.TYPE_HTML) as response:
        response.send(f"{webpage()}")

# change led state
@server.route("/led", method=HTTPMethod.POST)
def buttonpress(request: HTTPRequest):
    #  get query params (doesn't handle all cases, use with caution
    query = {x[0] : x[1] for x in [x.split("=") for x in request.body.decode("utf8").split("&")]}
    #  if the led on button was pressed
    if "LED" in query:
        #  turn on or off the onboard LED
        led.value = (query["LED"] == "ON")
    # Acknowledge
    with HTTPResponse(request, content_type=MIMEType.TYPE_HTML) as response:
        response.send()

# get temperature
@server.route("/temp")
def temp(request: HTTPRequest):
    # Read temperature
    temp = str(microcontroller.cpu.temperature)

    with HTTPResponse(request, content_type=MIMEType.TYPE_HTML) as response:
        response.send(temp)

# get stopwatch time
@server.route("/stopwatch")
def stopwatch(request: HTTPRequest):
    # Format last time clicked
    global last_clicked
    diff_time = datetime.now() - last_clicked

    with HTTPResponse(request, content_type=MIMEType.TYPE_HTML) as response:
        response.send(str(diff_time))

    # Update last clicked
    last_clicked = datetime.now()

print("Starting server..")
# startup the server
try:
    server.start(str(wifi.radio.ipv4_address))
    print("Listening on http://%s:80" % wifi.radio.ipv4_address)
#  if the server fails to begin, restart the pico w
except OSError:
    time.sleep(5)
    print("Restarting..")
    microcontroller.reset()

while True:
    try:
        #  poll the server for incoming/outgoing requests
        server.poll()
    except Exception as e:
        print(e)
        continue
