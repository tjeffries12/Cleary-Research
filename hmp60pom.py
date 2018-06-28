# This code is to run the HMP60 reading A0 as Relative Humidity and A1 as Temperature in degree Celcius 
import time;
import sys
import serial           #for POM serial conection
import time, datetime
from graphics import*   # Import the graphics library
import Adafruit_ADS1x15 # Import the ADS1x15 module, for the ADC
#import socket
from subprocess import check_output
global ha, ta, Oz
from mysql.connector import MySQLConnection, Error
from python_test_connector import read_db_config

#Initalized the relative humidity (ha) & temperature (ta) to 0
ha = 0
ta = 0
Oz = 0
Ip = (check_output(['hostname', '-I']))

#Sets up display window 
win = GraphWin("HMP60 live-stream", 900,500)
win.setBackground("white")

#Builds rectangles to act as plots of Humidity and Temperature
lR = Rectangle(Point(40,15),Point(750,100))
rR = Rectangle(Point(40,200),Point(750,300))
bR = Rectangle(Point(40,400),Point(750,500))
lR.setWidth(10)   #sets width of rectangle boxes
rR.setWidth(10)   #same as above
bR.setWidth(10)	  #same as above

#Builds text to read the current RH and T
H = Text(Point(200,50),"Relative Humidity (%): ")
T = Text(Point(200,250),"Temperature (C): ")
O = Text(Point(200,450),"Ozone (ppb): ")
IP = Text(Point(200,150),"IP Address: ")
IPin= Text(Point(470,150),'%s'%Ip)
Hin = Text(Point(470,50),'%s'%ha)
Tin = Text(Point(470,250), '%s'%ta)
Ozin = Text(Point(470,450),'%s'%Oz)
#sets font sizes for text
H.setSize(18)
T.setSize(18)
O.setSize(18)
IP.setSize(18)
Hin.setSize(22)
Tin.setSize(22)
Ozin.setSize(22)
IPin.setSize(18)
#Draws rectagles and font onto the window
H.draw(win)
T.draw(win)
O.draw(win)
IP.draw(win)
lR.draw(win)
rR.draw(win)
bR.draw(win)
Hin.draw(win)
Tin.draw(win)
Ozin.draw(win)
IPin.draw(win)
#Defines program start time
start_time =  time.asctime(time.localtime(time.time()))

#Creates File to save data to with current Timestamp 
f = open('%s'%start_time, 'w')

# Creates an ADS1115 ADC (12-bit) instance.
adc = Adafruit_ADS1x15.ADS1015()

#  - 2/3 = +/-6.144V
#  -   1 = +/-4.096V
#  -   2 = +/-2.048V
#  -   4 = +/-1.024V
#  -   8 = +/-0.512V
#  -  16 = +/-0.256V
GAIN = 4

#Definition program that opens mysql server and inputs data
def insert_readings(rh, temp,ozone):
    query = "UPDATE Pomhmp60 SET rh= %s, temp= %s , ozone = %s " \
            "WHERE id = '1'"
    args = (rh, temp, ozone)
 
    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)
 
#        if conn.is_connected():
#            print('connection established.')
#        else:
#            print('connection failed.')

        cursor = conn.cursor()
        cursor.execute(query, args)
 
#        if cursor.lastrowid:
#            print('last insert id', cursor.lastrowid)
#        else:
#            print('last insert id not found')
 
        conn.commit()
    except Error as error:
        print(error)
 
    finally:
        cursor.close()
        conn.close()

#This if statement searches and sets USB port
if '/dev/ttyUSB1' is 'pl2303':
	port = '/dev/ttyUSB1'
else: 
	port = '/dev/ttyUSB0'


#Create POM serial Object
pom = serial.Serial(
	port = port,
	baudrate = 19200,
	parity = serial.PARITY_NONE,
	stopbits = serial.STOPBITS_ONE,
	timeout = 10
	)

print('Reading ADC values, press Ctrl-C to quit...')
print(' ')
print('IP Address for Viewing Live Data')
print(Ip)
print>> f, '|      RH (%)   |     Temp C    |     O3 (ppb)     |   Time & Date   '
print>> f, ' '

while True:
# Read all the ADC channel values in a list.
	values = [0]*2
	ha = 0 
	ta = 0
	for i in range(10):	
		for i in range(2):
# Read ADC channels
			values[i] = adc.read_adc(i, gain=GAIN)	#reads values in array
			values[0] = (values[0]+29.367)/19.592	#relative humidity calibration
			values[1] = (values[1]-808.97)/17.521   #temperature (Celcius) calibration 
		ha = values[0]+ha 
		ta = values[1]+ta
		time.sleep(1)
	ha = ha/10 #averages 10 readings
	ta = ta/10 #averages 10 readings
     	POM = pom.readline() #reads whole line of data of POM
	localtime = time.asctime(time.localtime(time.time()))
	p = POM.split(',')
	Oz = p[0]
# Print the ADC values.

	print >> f,ha,',',ta,',',Oz,',',localtime,',' #prints to file
	print "|",ha,"|",ta,"|",Oz,"|",localtime #prints to command line

	Hin.setText('%s'%ha)
	Tin.setText('%s'%ta)
	Ozin.setText('%s'%Oz)

	rh =ha
	temp = ta
	ozone =Oz
	insert_readings(rh,temp ,ozone) # Inserts Data Values into MySQL server
win.getMouse()
win.close()
f.close()


