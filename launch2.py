from time import gmtime, strftime
from datetime import datetime

import sweepconfig

# -*- coding: utf-8 -*-
"""
Automatic code generated by FoV Sweep Configurator tool
It creates a python script that commands the sweep actions and
triggers the frame acquistion shots for the configured FoV 
scanning action.
It is base (apart from python) in OpenCv.
To be successfully executed, you must provide local functions 
to give to this script the exact information needed (video source number)
and the functions to move the motors, this must included in a custom
module called "sweepsupport".
"""
if sweepconfig.cte_use_cvcam:
    import cv2

if sweepconfig.cte_use_photocam:
    import subprocess

if sweepconfig.cte_use_gphoto2:
    import gphoto2capture

import sqlite3
import sweepsupport as sws
import urllib

def import_URL(URL):
    exec urllib.urlopen(URL).read() in globals()

####### Functions API ################

### Commands the motor to the position of that step
def commandMotor(x,y):
    if (sweepconfig.cte_verbose):
      print ("Sweep step X: " + str(x) + " Y: " + str(y))
      return sws.commandMotor(x,y)

### Investigate if the current step has been executed
### you can also include here the user interaction, allowing
### him/her to quit the scanning operation
def stepDone():
    # Wait for command or step time
    # returns are:
    #   -1 if the sweep operation must be cancelled
    #   1 if the step has been done and the frame must be acquired
    #   0 does nothing, non blocking implementation is welcome
    return sws.stepDone()

sqlsentence ="INSERT INTO \"sweep_ex_logs\" (\"step\", \"x\", \"y\", \"x_coord\", \"y_coord\", \"mx\", \"my\", \"mcomp\", \"mx_fdback\", \"my_fdback\", \"mcomp_fdback\", \"timestr\", \"sweep_eng_run_id\", \"dtinit\", \"dtend\", \"created_at\", \"updated_at\") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "

sqlprepare="CREATE TABLE IF NOT EXISTS \"sweep_ex_logs\" (\"id\" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, \"mx\" float, \"my\" float, \"mcomp\" float, \"created_at\" datetime, \"updated_at\" datetime, \"sweep_eng_run_id\" integer, \"step\" integer, \"x\" integer, \"y\" integer, \"x_coord\" float, \"y_coord\" float, \"timestr\" varchar, \"dtinit\" datetime, \"dtend\" datetime, \"mx_fdback\" float, \"my_fdback\" float, \"mcomp_fdback\" float);"

def dbinsert(dbc, curStep, stepX, stepY,stepXcoord,stepYcoord,mx,my,mcomp,mx_fdback,my_fdback,mcomp_fdback,timestr,dtinit,dtcam):
    item = [curStep,stepX,stepY,stepXcoord,stepYcoord,mx,my,mcomp,mx_fdback,my_fdback,mcomp_fdback,timestr,
            sweep_ex_id,dtinit,dtcam,dtcam,dtcam]
    dbc.execute(sqlsentence,item)
    return True
    
def dbprepare(dbc):
    dbc.execute(sqlprepare)
    return True
    
###### END Functions ############

###### Automatically generated code ###########
sweep_ex_id = 2
steps = [ { 'c': (0),'x': (0),'y': (0),'x_coord': (0.0),'y_coord': (0.0) },{ 'c': (1),'x': (1),'y': (0),'x_coord': (0.0018),'y_coord': (0.0) },{ 'c': (2),'x': (1),'y': (1),'x_coord': (0.0018),'y_coord': (0.0008) },{ 'c': (3),'x': (0),'y': (1),'x_coord': (0.0),'y_coord': (0.0008) },{ 'c': (4),'x': (-1),'y': (1),'x_coord': (-0.0018),'y_coord': (0.0008) },{ 'c': (5),'x': (-1),'y': (0),'x_coord': (-0.0018),'y_coord': (0.0) },{ 'c': (6),'x': (-1),'y': (-1),'x_coord': (-0.0018),'y_coord': (-0.0008) },{ 'c': (7),'x': (0),'y': (-1),'x_coord': (0.0),'y_coord': (-0.0008) } ]

###### Automatically generated steps table ###########
###### END Automatically generated code ###########


#### START EXECUTION ######

# Prepare the scan loop
curStep=0
done=0
# Create timestamp
timestr=strftime("%Y%m%d%H%M%S", gmtime())

if sweepconfig.cte_use_cvcam:
    # Cam has the video source
    cam = cv2.VideoCapture(sweepconfig.cte_camsource)
    if (sweepconfig.cte_verbose):
        print ("Camera resolution:")
        print ("* Horizontal: " + str(cam.get(cv2.CAP_PROP_FRAME_WIDTH)))
        print ("* Vertical: "+ str(cam.get(cv2.CAP_PROP_FRAME_HEIGHT)))

    #subprocess.check_call("exit 1", shell=True)
# Prepare the Database
db = sqlite3.connect('./db/log.sqlite3')
if not(db):
    ret = False
else:
    ret = True
    dbc = db.cursor()
    ret=dbprepare(dbc)
    
if (ret==False):
    done = -1
    print "Database ERROR! Aborting"

if (sweepconfig.cte_disable_motors_first):
    sws.disableMotors()

if (sweepconfig.cte_reset_motors_first):
    sws.resetMotors()

# Steps loop
# until ESC key is pressed
# or steps have finished
endStep = len(steps)
#endStep = 4
while (done!=-1 and curStep < endStep ):
    # In stepX and stepY we have the step positions to be done
    stepX=steps[curStep]['x']
    stepY=steps[curStep]['y']
    stepXcoord=steps[curStep]['x_coord']
    stepYcoord=steps[curStep]['y_coord']
    # Command motor position for this step
    dtinit = datetime.now()
    done,mx,my,mcomp=commandMotor(stepXcoord,stepYcoord)
    # Wait command to end
    while (done==0):
        done=stepDone();
    # END Command motor position for this step    
    if (done!=-1):
        # Acquire image
        dtcam = datetime.now()
        if sweepconfig.cte_use_cvcam:
            ret, frame = cam.read()
            #save to disk
            strg=sweepconfig.cte_fileprefix+'%s_%03d_%03d.png' % (timestr, sweep_ex_id, curStep)
            cv2.imwrite(sweepconfig.cte_framePath + strg, frame)
            #show the image
            cv2.imshow('Current Frame', frame)
        if sweepconfig.cte_use_photocam:
            # We configure the image capture
            strg='D%s_%03d_%03d.jpg' % (timestr, sweep_ex_id, curStep)
            cmd=sweepconfig.cte_cameractrl_path+sweepconfig.cte_cameractrl_command
            args=sweepconfig.cte_cameractrl_filenamecmd+" "+strg
            print("Photo set filename: "+cmd+" "+args)
            subprocess.check_output([cmd,args])
            args=sweepconfig.cte_cameractrl_capturecmd
            print("Photo capture frame: "+cmd+" "+args)
            subprocess.check_output([cmd,args])
        if sweepconfig.cte_use_gphoto2:
            strg=sweepconfig.cte_gphoto2_filename_root+'%s_%03d_%03d.jpg' % (timestr, sweep_ex_id, curStep)
            gphoto2capture.capture(sweepconfig.cte_gphoto2_framePath,strg,False)
        # acquire the motor status
        mx_fdback,my_fdback,mcomp_fdback = sws.motorPositions()
        print ("Motor | mx: "+str(mx_fdback)+", my: "+str(my_fdback)+", mcomp: "+str(mcomp_fdback))
        # Web information upload
        #r = requests.post("http://localhost:3000/sweep_eng_runs/1/sweep_ex_logs/new", data={'sweep_ex_log': {"sweep_eng_run_id":"1", "a":"6", "b":"8", "c":"9"},"sweep_eng_run_id":"1" })
        #print(r.status_code, r.reason)
        # BD information store
        done=dbinsert(dbc,curStep, stepX, stepY,stepXcoord, stepYcoord,mx,my,mcomp,mx_fdback,my_fdback,mcomp_fdback,timestr,dtinit,dtcam)
        curStep += 1

# End of program, steps have finished or someone has cancelled the scan process
if (curStep < len(steps)):
  # Scan process was cancelled
    if (sweepconfig.cte_verbose):
        print ("Scan process was cancelled")
        dummy=0 # Dummy for avoiding indentation failures

db.commit()
db.close()
if sweepconfig.cte_use_cvcam:
    cam.release()
    cv2.destroyAllWindows()
sws.motorClose()
