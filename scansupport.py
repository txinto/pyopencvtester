import scanconfig
import sys
sys.path.insert(0, './fsm')
import FoV

from scancalib import *
from BitManipulation import *

if scanconfig.cte_use_cvcam:
    import cv2

########### XPORT SIDE #################


# Sends an escape char to clear the Xport channel
def resetXport():
    if scanconfig.cte_use_socket:
        str = "" + chr(27)
        FoV.dre.ser.sendall(str)
        sendMotorCommand("@")
        r=getMotorResponse()


# Sends an XPort command, and process its response
# while waiting for the response, also processes the probable
# pending Ok's and P's
def sendXportCmd(str):
    global numberOfOkToRx
    global numberOfPToRx
    sendMotorCommand(str)
    if scanconfig.cte_verbose:
        print("XportCmd>" + str)
    done = False
    while not (done):
        r = getMotorResponse()
        if scanconfig.cte_verbose:
            print("XPortResponse>" + r + "< nothing?")
        done = (len(r) == 0)
        if not (done):
            processPendingResponse(r)


# Sends the addressing XPort command, and process it response
# while waiting for the response, also processes the probable
# pending Ok's and P's
def sendXportBegin(m):
    if (scanconfig.cte_use_socket):
        cmd_str = "#" + str(m)
        sendXportCmd(cmd_str)


# Sends the END of addressing XPort command, and process it response
# while waiting for the response, also processes the probable
# pending Ok's and P's
def sendXportEnd():
    if (scanconfig.cte_use_socket):
        cmd_str = "@"
        sendXportCmd(cmd_str)


########## COMM PROTOCOL #############


# Gets a response from the Motors
def getMotorResponse():
    FoV.getCtrlResponse()
    return FoV.dre.command_rx_buf


# Sends a command to the Motors
def sendMotorCommand(cmd_str):
    #ser.write(cmd_str+chr(13))
    if scanconfig.cte_verbose:
        print "Command sent: "+cmd_str
    FoV.dre.command_tx_buf = cmd_str
    FoV.sendCtrlCommand()


## PENDING RESPONSES SECTION ########

numberOfPToRx = 0       # Number of pending P responses
numberOfOkToRx = 0      # Number of pending Ok responses

# Processes the given response to decrement the pending Ok's and pending P's
def processPendingResponse(r):
    global numberOfOkToRx
    global numberOfPToRx
    if scanconfig.cte_verbose:
        print("Resp2:" + r)
    if (r == "p"):
        if scanconfig.cte_wait_for_p:
            numberOfPToRx -= 1
    if (r == "OK"):
        numberOfOkToRx -= 1
    if scanconfig.cte_verbose:
        print("Number of pending P to Rx: " + str(numberOfPToRx))
        print("Number of pending Ok to Rx: " + str(numberOfOkToRx))


# Sets the number of pending responses to zero Ok's and zero P's
def resetPendingResponses():
    global numberOfOkToRx
    global numberOfPToRx
    numberOfPToRx = 0
    numberOfOkToRx = 0


# Reads a response and processes it, decrementing pending P's and pending Ok's
def consumeResponse():
    global numberOfOkToRx
    global numberOfPToRx
    r = getMotorResponse()
    processPendingResponse(r)


# Reads as many responses needed to receive all the pending Ok's
# While reading the responses, it also decrements the count of pending P's
def consumePendingOks():
    global numberOfOkToRx
    global numberOfPToRx
    while (numberOfOkToRx > 0):
        consumeResponse()
    if (numberOfOkToRx == 0):
        ret = 0
    else:
        ret = -1
    return ret


# Reads as many responses needed to receive all the pending P's
# While reading the responses, it also decrements the count of pending Ok's
def consumePendingPs():
    global numberOfOkToRx
    global numberOfPToRx
    if scanconfig.cte_wait_for_p:
        while (numberOfPToRx > 0):
            consumeResponse()
        if (numberOfPToRx == 0):
            ret = 0
        else:
            ret = -1
    else:
        ret = 0
    return ret


# Increments the count of pending P responses
def incrementPendingP():
    global numberOfPToRx
    if scanconfig.cte_wait_for_p:
        numberOfPToRx += 1


# Increments the count of pending Ok responses
def incrementPendingOk():
    global numberOfOkToRx
    numberOfOkToRx += 1


############ MOTOR ACTIONS SECTION #############

# Sends to Home the motor identified with the given index
def goHome(idx):
        # Programming the Home speeds
        cmd_str = prefixX+"HOSP-%3d" % (cte_vh[idx])
        sendMotorCommand(cmd_str)
        if scanconfig.cte_verbose:
            print("Command:"+cmd_str)
        incrementPendingOk()
        consumePendingOks()

        cmd_str = prefixX+"APL0"
        sendMotorCommand(cmd_str)
        if scanconfig.cte_verbose:
            print("Command:"+cmd_str)
        incrementPendingOk()
        consumePendingOks()

        if (scanconfig.cte_command_np_flags):
            cmd_str = prefixX + "NP"
            sendMotorCommand(cmd_str)
            if scanconfig.cte_verbose:
                print("Command:"+cmd_str)
            incrementPendingOk()
            consumePendingOks()
            incrementPendingP()

        cmd_str = prefixX + "GOHOSEQ"
        sendMotorCommand(cmd_str)
        if scanconfig.cte_verbose:
            print("Command:"+cmd_str)
        incrementPendingOk()
        consumePendingOks()
        consumePendingPs()

        cmd_str = prefixX+"HOSP%3d" % (cte_vi[idx])
        sendMotorCommand(cmd_str)
        if scanconfig.cte_verbose:
            print("Command:"+cmd_str)
        incrementPendingOk()
        consumePendingOks()

        if (scanconfig.cte_command_np_flags):
            cmd_str = prefixX + "NP"
            sendMotorCommand(cmd_str)
            if scanconfig.cte_verbose:
                print("Command:"+cmd_str)
            incrementPendingOk()
            consumePendingOks()
            incrementPendingP()

        cmd_str = prefixX + "GOIX"
        sendMotorCommand(cmd_str)
        if scanconfig.cte_verbose:
            print("Command:"+cmd_str)
        incrementPendingOk()
        consumePendingOks()
        consumePendingPs()

        cmd_str = prefixX+"APL1"
        sendMotorCommand(cmd_str)
        if scanconfig.cte_verbose:
            print("Command:"+cmd_str)
        incrementPendingOk()
        consumePendingOks()

        cmd_str = prefixX+"HOSP-%3d" % (cte_vh[idx])
        sendMotorCommand(cmd_str)
        if scanconfig.cte_verbose:
            print("Command:"+cmd_str)
        incrementPendingOk()
        consumePendingOks()


# Sends to Home the motor assigned to X movements
def goHomeMx():
    if (scanconfig.cte_use_motor_x):
        sendXportBegin(scanconfig.cte_motor_x_xport)
        goHome(scanconfig.cte_motor_x - 1)
        sendXportEnd()


# Sends to Home the motor assigned to Y movements
def goHomeMy():
    if (scanconfig.cte_use_motor_y):
        sendXportBegin(scanconfig.cte_motor_y_xport)
        goHome(scanconfig.cte_motor_y - 1)
        sendXportEnd()


# Sends to Home the motor assigned to compensation movements
def goHomeMcomp():
    if (scanconfig.cte_use_motor_comp):
        sendXportBegin(scanconfig.cte_motor_comp_xport)
        goHome(scanconfig.cte_motor_comp - 1)
        sendXportEnd()


def commandLSx(setpoint, blocking = True):
    # Program the motor to warn when the command is done
    if (scanconfig.cte_use_motor_x):
        if (abs(setpoint - current_pos_x) > cte_tol_x):
            sendXportBegin(scanconfig.cte_motor_x_xport)

            if (scanconfig.cte_command_np_flags and blocking):
                cmd_str = prefixX + "NP"
                sendMotorCommand(cmd_str)
                if scanconfig.cte_verbose:
                    print("Command:" + cmd_str)
                incrementPendingOk()
                consumePendingOks()
                incrementPendingP()

            cmd_str = prefixX + "LA%04d" % (setpoint)
            sendMotorCommand(cmd_str)
            if scanconfig.cte_verbose:
                print("Command:" + cmd_str)
            incrementPendingOk()
            consumePendingOks()

            # Move the motor
            cmd_str = prefixX + "M"
            sendMotorCommand(cmd_str)
            if scanconfig.cte_verbose:
                print("Command:" + cmd_str)
            incrementPendingOk()
            consumePendingOks()

            # Wait for command responses
            if (blocking):
                ret = consumePendingPs()
            sendXportEnd()
        else:
            if scanconfig.cte_verbose:
                print("Cancelo pues Pos actual: " + str(current_pos_x) + " parecida a orden: " + str(setpoint))


def commandLSy(setpoint, blocking = True):
    if (scanconfig.cte_use_motor_y):
        if (abs(setpoint - current_pos_y) > cte_tol_y):
            sendXportBegin(scanconfig.cte_motor_y_xport)

            # Program the motor to warn when the command is done
            if (scanconfig.cte_command_np_flags and blocking):
                cmd_str = prefixY + "NP"
                sendMotorCommand(cmd_str)
                if scanconfig.cte_verbose:
                    print("Command:" + cmd_str)
                incrementPendingOk()
                consumePendingOks()
                incrementPendingP()

            cmd_str = prefixY + "LA%04d" % (setpoint)
            sendMotorCommand(cmd_str)
            if scanconfig.cte_verbose:
                print("Command:" + cmd_str)
            incrementPendingOk()
            consumePendingOks()

            cmd_str = prefixY + "M"
            sendMotorCommand(cmd_str)
            if scanconfig.cte_verbose:
                print("Command:" + cmd_str)
            incrementPendingOk()
            consumePendingOks()

            # Wait for command responses
            if (blocking):
                ret = consumePendingPs()

            sendXportEnd()
        else:
            if scanconfig.cte_verbose:
                print("Cancelo pues Pos actual: " + str(current_pos_y) + " parecida a orden: " + str(setpoint))


def commandLScomp(setpoint, blocking = True):
    if (scanconfig.cte_use_motor_comp):
        if (abs(setpoint - current_pos_comp) > cte_tol_comp):
            sendXportBegin(scanconfig.cte_motor_comp_xport)
            # Program the motor to warn when the command is done
            if (scanconfig.cte_command_np_flags and blocking):
                cmd_str = prefixComp + "NP"
                sendMotorCommand(cmd_str)
                if scanconfig.cte_verbose:
                    print("Command:" + cmd_str)
                incrementPendingOk()
                consumePendingOks()
                incrementPendingP()

            cmd_str = prefixComp + "LA%04d" % (setpoint)
            sendMotorCommand(cmd_str)
            if scanconfig.cte_verbose:
                print("Command:" + cmd_str)
            incrementPendingOk()
            consumePendingOks()

            cmd_str = prefixComp + "M"
            sendMotorCommand(cmd_str)
            if scanconfig.cte_verbose:
                print("Command:" + cmd_str)
            incrementPendingOk()
            consumePendingOks()

            # Wait for command responses
            if (blocking):
                ret = consumePendingPs()

            sendXportEnd()
        else:
            if scanconfig.cte_verbose:
                print("Cancelo pues Pos actual: " + str(current_pos_comp) + " parecida a orden: " + str(setpoint))


# Commands the window to x and y position (in mm from centered position)
# It calculates the needed commands for Mx, My and Mcomp motors and sends them.
def commandMotorUnits(x, y, z):
    ret = 0
    # Compute compensation
    lscomp = z
    # Compute LSX and LSY
    lsx_temp = x
    lsx_pos = max(min(lsx_temp, cte_lsx_max), cte_lsx_min)
    lsy_temp = y
    lsy_pos = max(min(lsy_temp, cte_lsy_max), cte_lsy_min)
    lscomp_temp = z
    lscomp_pos = max(min(lscomp_temp, cte_lscomp_max), cte_lscomp_min)

    if (lsx_temp != lsx_pos or
                lsy_temp != lsy_pos or
                lscomp_temp != lscomp_pos):
        if scanconfig.cte_verbose:
            print "Error on calculating position: out of range of LS motors"
            print "X: %f Y: %f" % (x, y)
            print "LSX_TEMP: %.2f LSY_TEMP: %.2f LSCOMP_TEMP: %.2f" % (lsx_temp, lsy_temp, lscomp_temp)
            print "LSX_POS: %.2f LSY_POS: %.2f LSCOMP_POS: %.2f" % (lsx_pos, lsy_pos, lscomp_pos)

        ret = -1
    else:
        xDict = {'Name': 'x', 'Function': commandLSx, 'Argument': lsx_pos,
                 'Delta': abs(lsx_pos - current_pos_x) / (float(cte_vx) / 100.0),
                 'Blocking': False}
        yDict = {'Name': 'y', 'Function': commandLSy, 'Argument': lsy_pos,
                 'Delta': abs(lsy_pos - current_pos_y) / (float(cte_vy) / 100.0),
                 'Blocking': False}
        compDict = {'Name': 'comp', 'Function': commandLScomp, 'Argument': lscomp_pos,
                    'Delta': abs(lscomp_pos - current_pos_comp) / (float(cte_vcomp) / 100.0),
                    'Blocking': False}
        reordDict = [xDict, yDict, compDict]
        # send the commands
        newlist = sorted(reordDict, key=lambda k: k['Delta'])
        newlist[len(newlist) - 1]['Blocking'] = True
        for func in newlist:
            print("Ord: " + func['Name'] + ", Delta:" + str(func['Delta']) + ", blocking:" + str(
                func['Blocking']))
            (func['Function'])(func['Argument'], func['Blocking'])
    return ret, lsx_pos, lsy_pos, lscomp_pos

def commandMotorMot(xMot,yMot):
	x=(xMot-cte_lsx_zero)/cte_lsx_scale
	y=(yMot-cte_lsy_zero)/cte_lsy_scale
        print "x: %.6f y: %.6f" % (x, y)
	ret, lsx_pos, lsy_pos, lscomp_pos = commandMotor(x,y)
        print "LSX_TEMP: %.2f LSY_TEMP: %.2f LSCOMP_TEMP: %.2f" % (lsx_pos, lsy_pos, lscomp_pos)

# Commands the window to x and y position (in mm from centered position)
# It calculates the needed commands for Mx, My and Mcomp motors and sends them.
def commandMotor(x, y):
    ret = 0
    # Compute compensation
    lscomp = ((cte_comp_factor_x * x) + (cte_comp_factor_x * y)) / cte_comp_divisor
    # Compute LSX and LSY
    lsx_temp = cte_lsx_zero + (x * cte_lsx_scale)
    lsx_pos = max(min(lsx_temp, cte_lsx_max), cte_lsx_min)
    lsy_temp = cte_lsy_zero + (y * cte_lsy_scale)
    lsy_pos = max(min(lsy_temp, cte_lsy_max), cte_lsy_min)
    lscomp_temp = cte_lscomp_zero + (lscomp * cte_lscomp_scale)
    lscomp_pos = max(min(lscomp_temp, cte_lscomp_max), cte_lscomp_min)

    if (lsx_temp != lsx_pos or
                lsy_temp != lsy_pos or
                lscomp_temp != lscomp_pos):
        if scanconfig.cte_verbose:
            print "Error on calculating position: out of range of LS motors"
            print "X: %f Y: %f" % (x, y)
            print "LSX_TEMP: %.2f LSY_TEMP: %.2f LSCOMP_TEMP: %.2f" % (lsx_temp, lsy_temp, lscomp_temp)
            print "LSX_POS: %.2f LSY_POS: %.2f LSCOMP_POS: %.2f" % (lsx_pos, lsy_pos, lscomp_pos)

        ret = -1
    else:
        xDict = {'Name': 'x', 'Function': commandLSx, 'Argument': lsx_pos, 'Delta': abs(lsx_pos-current_pos_x)/(float(cte_vx)/100.0),
                 'Blocking': False}
        yDict = {'Name': 'y', 'Function': commandLSy, 'Argument': lsy_pos, 'Delta': abs(lsy_pos-current_pos_y)/(float(cte_vy)/100.0),
                 'Blocking': False}
        compDict = {'Name': 'comp', 'Function': commandLScomp, 'Argument': lscomp_pos,
                    'Delta': abs(lscomp_pos-current_pos_comp)/(float(cte_vcomp)/100.0), 'Blocking': False}
        if scanconfig.cte_force_wait_for_motor == 0 :
            reordDict=[xDict, yDict, compDict]
            # send the commands
            newlist = sorted(reordDict, key=lambda k: k['Delta'])

        else:
            if scanconfig.cte_force_wait_for_motor == 1 :
                newlist = [yDict, compDict, xDict]
            else:
                if scanconfig.cte_force_wait_for_motor == 2 :
                    newlist = [xDict, compDict, yDict]
                else:
                    if scanconfig.cte_force_wait_for_motor >= 3 :
                        newlist = [xDict, yDict, compDict]

        newlist[len(newlist) - 1]['Blocking'] = True
        for func in newlist:
            print("Ord: " + func['Name'] + ", Delta:" + str(func['Delta']) + ", blocking:" + str(func['Blocking']))
            (func['Function'])(func['Argument'], func['Blocking'])

    return ret, lsx_pos, lsy_pos, lscomp_pos


# Commands the window to x and y position (in mm from centered position)
# It calculates the needed commands for Mx, My and Mcomp motors and sends them.
def commandMotorComp(x, y):
    ret = 0
    # Compute compensation
    lscomp = ((cte_comp_factor_x * x) + (cte_comp_factor_x * y)) / cte_comp_divisor
    # Compute LSX and LSY
    lsx_temp = cte_lsx_zero + (x * cte_lsx_scale)
    lsx_pos = max(min(lsx_temp, cte_lsx_max), cte_lsx_min)
    lsy_temp = cte_lsy_zero + (y * cte_lsy_scale)
    lsy_pos = max(min(lsy_temp, cte_lsy_max), cte_lsy_min)
    lscomp_temp = cte_lscomp_zero + (lscomp * cte_lscomp_scale)
    lscomp_pos = max(min(lscomp_temp, cte_lscomp_max), cte_lscomp_min)

    if (lsx_temp != lsx_pos or
                lsy_temp != lsy_pos or
                lscomp_temp != lscomp_pos):
        if scanconfig.cte_verbose:
            print "Error on calculating position: out of range of LS motors"
            print "X: %f Y: %f" % (x, y)
            print "LSX_TEMP: %.2f LSY_TEMP: %.2f LSCOMP_TEMP: %.2f" % (lsx_temp, lsy_temp, lscomp_temp)
            print "LSX_POS: %.2f LSY_POS: %.2f LSCOMP_POS: %.2f" % (lsx_pos, lsy_pos, lscomp_pos)

        ret = -1
    else:
        xDict = {'Name': 'x', 'Function': commandLSx, 'Argument': lsx_pos, 'Delta': abs(lsx_pos-current_pos_x)/(float(cte_vx)/100.0),
                 'Blocking': False}
        yDict = {'Name': 'y', 'Function': commandLSy, 'Argument': lsy_pos, 'Delta': abs(lsy_pos-current_pos_y)/(float(cte_vy)/100.0),
                 'Blocking': False}
        compDict = {'Name': 'comp', 'Function': commandLScomp, 'Argument': lscomp_pos,
                    'Delta': abs(lscomp_pos-current_pos_comp)/(float(cte_vcomp)/100.0), 'Blocking': False}
        reordDict = [compDict]
        # send the commands
        newlist = reordDict
        newlist[len(newlist)-1]['Blocking'] = True
        for func in newlist:
            print("Ord: "+func['Name']+", Delta:"+str(func['Delta'])+", blocking:"+str(func['Blocking']))
            (func['Function'])(func['Argument'], func['Blocking'])
    return ret, lsx_pos, lsy_pos, lscomp_pos


# Commands the window to x and y position (in mm from centered position)
# It calculates the needed commands for Mx, My and Mcomp motors and sends them.
def commandMotorWindow(x, y):
    ret = 0
    # Compute compensation
    lscomp = ((cte_comp_factor_x * x) + (cte_comp_factor_x * y)) / cte_comp_divisor
    # Compute LSX and LSY
    lsx_temp = cte_lsx_zero + (x * cte_lsx_scale)
    lsx_pos = max(min(lsx_temp, cte_lsx_max), cte_lsx_min)
    lsy_temp = cte_lsy_zero + (y * cte_lsy_scale)
    lsy_pos = max(min(lsy_temp, cte_lsy_max), cte_lsy_min)
    lscomp_temp = cte_lscomp_zero + (lscomp * cte_lscomp_scale)
    lscomp_pos = max(min(lscomp_temp, cte_lscomp_max), cte_lscomp_min)

    if (lsx_temp != lsx_pos or
                lsy_temp != lsy_pos or
                lscomp_temp != lscomp_pos):
        if scanconfig.cte_verbose:
            print "Error on calculating position: out of range of LS motors"
            print "X: %f Y: %f" % (x, y)
            print "LSX_TEMP: %.2f LSY_TEMP: %.2f LSCOMP_TEMP: %.2f" % (lsx_temp, lsy_temp, lscomp_temp)
            print "LSX_POS: %.2f LSY_POS: %.2f LSCOMP_POS: %.2f" % (lsx_pos, lsy_pos, lscomp_pos)
        ret = -1
    else:
        xDict = {'Name': 'x', 'Function': commandLSx, 'Argument': lsx_pos, 'Delta': abs(lsx_pos-current_pos_x),
                 'Blocking': False}
        yDict = {'Name': 'y', 'Function': commandLSy, 'Argument': lsy_pos, 'Delta': abs(lsy_pos-current_pos_y),
                 'Blocking': False}
        compDict = {'Name': 'comp', 'Function': commandLScomp, 'Argument': lscomp_pos,
                    'Delta': abs(lscomp_pos-current_pos_comp), 'Blocking': False}
        reordDict=[xDict,yDict]
        # send the commands
        newlist = sorted(reordDict, key=lambda k: k['Delta'])
	newlist[len(newlist)-1]['Blocking'] = True
    	for func in newlist:
        	print("Ord: "+func['Name']+", Delta:"+str(func['Delta'])+", blocking:"+str(func['Blocking']))
        	(func['Function'])(func['Argument'], func['Blocking'])

    return ret, lsx_pos, lsy_pos, lscomp_pos


# Commands home for all the motors, and then puts the window at the central position.
def resetMotors():
    goHomeMx()
    goHomeMy()
    goHomeMcomp()

    # Calculate the center position of the window over the FoV
    lsx = 0.0
    lsy = 0.0

    print("lsx: "+str(lsx))
    print("lsy: "+str(lsy))
    
    commandMotor(lsx, lsy)


# Commands home for all the motors, and then puts the window at the central position.
def resetMotorsWindow():
    goHomeMx()
    goHomeMy()
#    goHomeMcomp()

    # Calculate the center position of the window over the FoV
    lsx = 0.0
    lsy = 0.0

    print("lsx: "+str(lsx))
    print("lsy: "+str(lsy))
    
    commandMotorWindow(lsx, lsy)


# Commands home for all the motors, and then puts the window at the central position.
def resetMotorsComp():
    #goHomeMx()
    #goHomeMy()
    goHomeMcomp()

    # Calculate the center position of the window over the FoV
    lsx = 0.0
    lsy = 0.0

    print("lsx: "+str(lsx))
    print("lsy: "+str(lsy))
    
    commandMotorComp(lsx, lsy)


# Disables the motors
def disableMotors():
    if (scanconfig.cte_use_motor_x):
        sendXportBegin(scanconfig.cte_motor_x_xport)
        cmd_str = prefixX + "DI"
        sendMotorCommand(cmd_str)
        if scanconfig.cte_verbose:
            print("Command:" + cmd_str)
        incrementPendingOk()
        consumePendingOks()
        sendXportEnd()

    if (scanconfig.cte_use_motor_y):
        sendXportBegin(scanconfig.cte_motor_y_xport)
        cmd_str = prefixY + "DI"
        sendMotorCommand(cmd_str)
        if scanconfig.cte_verbose:
            print("Command:" + cmd_str)
        incrementPendingOk()
        consumePendingOks()
        sendXportEnd()


    if (scanconfig.cte_use_motor_comp):
        sendXportBegin(scanconfig.cte_motor_comp_xport)
        cmd_str = prefixComp + "DI"
        sendMotorCommand(cmd_str)
        if scanconfig.cte_verbose:
            print("Command:" + cmd_str)
        incrementPendingOk()
        consumePendingOks()
        sendXportEnd()


# Disables the motors
def enableMotors():
    if (scanconfig.cte_use_motor_x):
        sendXportBegin(scanconfig.cte_motor_x_xport)
        cmd_str = prefixX + "EN"
        sendMotorCommand(cmd_str)
        if scanconfig.cte_verbose:
            print("Command:" + cmd_str)
        incrementPendingOk()
        consumePendingOks()
        sendXportEnd()

    if (scanconfig.cte_use_motor_y):
        sendXportBegin(scanconfig.cte_motor_y_xport)
        cmd_str = prefixY + "EN"
        sendMotorCommand(cmd_str)
        if scanconfig.cte_verbose:
            print("Command:" + cmd_str)
        incrementPendingOk()
        consumePendingOks()
        sendXportEnd()


    if (scanconfig.cte_use_motor_comp):
        sendXportBegin(scanconfig.cte_motor_comp_xport)
        cmd_str = prefixComp + "EN"
        sendMotorCommand(cmd_str)
        if scanconfig.cte_verbose:
            print("Command:" + cmd_str)
        incrementPendingOk()
        consumePendingOks()
        sendXportEnd()


# Waits for a defined time for user to press a key
def waitKey(t):
    '''
    import time, msvcrt
    startTime=time.time()

    print "Press any key or wait "+str(cte_waitTime)+" seconds"
    done = False
    ret = -1
    while not(done):
        if msvcrt.kbhit():
            ret=msvcrt.getch()
            done = True
        elif time.time() - startTime > t:
            done = True
    return ret
    '''
    return -1


# Checks if the scan step has been done.  It also returns if the scan has to be cancelled
def stepDone():
    # Wait for command or step time
    # it returns True if nobody presses the ESC
    if (scanconfig.cte_use_cvcam):
        key = cv2.waitKey(cte_stepTime)
    else:
        key = waitKey(cte_waitTime)
    if (key == 27):
        # Someone presses the ESC key, should return
        ret = -1
    else:
        if (key == -1):
            # Time expired
            if scanconfig.cte_force_wait_bit_y:
                my_finished = False
                while not stepFinishedYPoll():
                    stepFinishedYPoll()

            ret = 1

        else:
            # Another key presssed
            ret=0

    return ret


current_pos_x = 0
current_pos_y = 0
current_pos_comp = 0

mx_status = 0
my_status = 0
mcomp_status = 0

## Gets the status of the X motor
def getMotorStatusX():
    global mx_status

    # Obtain final positions
    if (scanconfig.cte_use_motor_x):
        sendXportBegin(scanconfig.cte_motor_x_xport)
        cmd_str = prefixX + "OST"
        sendMotorCommand(cmd_str)
        if scanconfig.cte_verbose:
            print("OSTCmd:" + cmd_str)
        r = getMotorResponse()
        if scanconfig.cte_verbose:
            print("OSTResp x:" + r)
        mx_status = int(r)
        sendXportEnd()
    else:
        mx_status = 0

## Gets the status of the Y motor
def getMotorStatusY():
    global my_status

    # Obtain final positions
    if (scanconfig.cte_use_motor_y):
        sendXportBegin(scanconfig.cte_motor_y_xport)
        cmd_str = prefixY + "OST"
        sendMotorCommand(cmd_str)
        if scanconfig.cte_verbose:
            print("OSTCmd:" + cmd_str)
        r = getMotorResponse()
        if scanconfig.cte_verbose:
            print("OSTResp y:" + r)
        my_status = int(r)
        sendXportEnd()
    else:
        my_status = 0

## Gets the status of the Comp motor
def getMotorStatusComp():
    global mcomp_status

    # Obtain final positions
    if (scanconfig.cte_use_motor_comp):
        sendXportBegin(scanconfig.cte_motor_comp_xport)
        cmd_str = prefixComp + "OST"
        sendMotorCommand(cmd_str)
        if scanconfig.cte_verbose:
            print("OSTCmd:" + cmd_str)
        r = getMotorResponse()
        if scanconfig.cte_verbose:
            print("OSTResp Comp:" + r)
        mcomp_status = int(r)
        sendXportEnd()
    else:
        mcomp_status = 0


def CheckBitPosAttained(word_to_check):
    return True


mx_finished = False;
my_finished = False;
mcomp_finished = False;

# Checks if the positions has been attained for motor X
def stepFinishedXPoll():
    global mx_finished;

    if not mx_finished:
        getMotorStatusX()
        mx_finished=testBit(mx_status, 11)

    return mx_finished


# Checks if the positions has been attained for motor X
def stepFinishedYPoll():
    global my_finished;

    if not my_finished:
        getMotorStatusY()
        my_finished=testBit(my_status, 11)

    return mx_finished


# Checks if the positions has been attained for motor Comp
def stepFinishedCompPoll():
    global mcomp_finished;

    if not mcomp_finished:
        getMotorStatusComp()
        mcomp_finished=testBit(mcomp_status, 11)

    return mcomp_finished


# Retrieves the position for each motor
def motorPositions():
    global current_pos_x
    global current_pos_y
    global current_pos_comp

    # Obtain final positions
    if (scanconfig.cte_use_motor_x):
        sendXportBegin(scanconfig.cte_motor_x_xport)
        cmd_str = prefixX + "POS"
        sendMotorCommand(cmd_str)
        if scanconfig.cte_verbose:
            print("PosCmd:" + cmd_str)
        r = getMotorResponse()
        # if scanconfig.cte_verbose:
        print("PosResp x:" + r)
        mx_fdback = int(r)
        current_pos_x = mx_fdback
        sendXportEnd()
    else:
        mx_fdback = -1

    if (scanconfig.cte_use_motor_y):
        sendXportBegin(scanconfig.cte_motor_y_xport)
        cmd_str = prefixY + "POS"
        sendMotorCommand(cmd_str)
        if scanconfig.cte_verbose:
            print("PosCmd:" + cmd_str)
        r = getMotorResponse()
        # if scanconfig.cte_verbose:
        print("PosResp y:" + r)
        my_fdback = int(r)
        current_pos_y = my_fdback
        sendXportEnd()
    else:
        my_fdback = -1

    if (scanconfig.cte_use_motor_comp):
        sendXportBegin(scanconfig.cte_motor_comp_xport)
        cmd_str = prefixComp + "POS"
        sendMotorCommand(cmd_str)
        if scanconfig.cte_verbose:
            print("PosCmd:" + cmd_str)
        r = getMotorResponse()
        # if scanconfig.cte_verbose:
        print("PosResp comp:" + r)
        mcomp_fdback = int(r)
        current_pos_comp = mcomp_fdback
        sendXportEnd()
    else:
        mcomp_fdback = -1

    return mx_fdback, my_fdback, mcomp_fdback


# Closes the communication with the motors
def motorClose():
    if not(scanconfig.cte_use_socket):
        ser.close()             # close port
    else:    
        sckt.close              # Close the socket when done    

cte_vh = [cte_vhx, cte_vhy, cte_vhcomp]
cte_vi = [cte_vix, cte_viy, cte_vicomp]
cte_v = [cte_vx, cte_vy, cte_vcomp]

########### MAIN INITIALIZATIONS ###############

# Indicates to the DRE (fsm data base) which kind of connection must be used
FoV.dre.cte_use_socket = scanconfig.cte_use_socket

# Opens the communication channel
if not (scanconfig.cte_use_socket):
    import serial

    cte_serial_port = scanconfig.cte_serial_port
    if scanconfig.cte_verbose:
        print "Chosen serial port: " + cte_serial_port
    ser = serial.Serial(
        port=cte_serial_port,
        baudrate=9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        rtscts=False,
        dsrdtr=False,
        xonxoff=True
    )
    FoV.dre.ser = ser
    resetPendingResponses()
else:
    import socket  # Import socket module

    sckt = socket.socket()  # Create a socket object
    sckt.connect((scanconfig.cte_socket_ip, scanconfig.cte_socket_port))
    FoV.dre.ser = sckt
    resetXport()
    resetPendingResponses()

if (scanconfig.cte_use_socket):
    prefixX = ""
    prefixY = ""
    prefixComp = ""
else:
    prefixX = str(scanconfig.cte_motor_x)
    prefixY = str(scanconfig.cte_motor_y)
    prefixComp = str(scanconfig.cte_motor_comp)

# Comando para calcular la posicion de compensacion en base a coordenadas de motores x e y
#commandMotorMot(11100.0,16400.0)

