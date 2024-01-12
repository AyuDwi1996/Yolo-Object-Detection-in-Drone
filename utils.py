import cv2
import numpy as np
from djitellopy import Tello
import time
import socket

whT = 320
confThreshold = 0.5
nmsThreshold = 0.3
classesFile = 'coco.names'
classNames = []
with open(classesFile, 'rt') as f:
    classNames = f.read().rstrip('\n').split('\n')

modelConfiguration = 'yolov3.cfg'
modelWeights = 'yolov3.weights'

net = cv2.dnn.readNetFromDarknet(modelConfiguration, modelWeights)
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

# Tello server address and port
tello_address = ('192.168.10.1', 8889)

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_command(command):
    try:
        # Send the command to Tello
        sock.sendto(command.encode(), tello_address)

        # Receive response from Tello
        response, _ = sock.recvfrom(1024)
        return response.decode()
    except Exception as e:
        print(str(e))
    return ''

def intializeTello():
    # CONNECT TO TELLO
    myDrone = Tello()
    # myDrone = Tello()
    # myDrone.PORT = 8889  # Use a different port number
    # myDrone.connect()
    myDrone.connect()
    myDrone.for_back_velocity = 0
    myDrone.left_right_velocity = 0
    myDrone.up_down_velocity = 0
    myDrone.yaw_velocity = 0
    myDrone.speed =0
    print(myDrone.get_battery())
    myDrone.streamoff()
    myDrone.streamon()
    time.sleep(2)
    # myDrone.takeoff()
    # myDrone.send_rc_control(0,0,0,0)
    # myDrone.send_rc_control(0, 0, 0, 0)
    # myDrone.send_rc_control(0, 0, 0, 0)
    # myDrone.send_rc_control(0, 0, 0, 0)
    return myDrone

def telloGetFrame(myDrone):
    frame = myDrone.get_frame_read().frame
    # frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    #
    # # Adjust hue, saturation, and brightness
    # frame_hsv[:, :, 0] += 30  # Adjust hue (you can experiment with different values)
    # frame_hsv[:, :, 1] += 30  # Adjust saturation
    # frame_hsv[:, :, 2] += 30  # Adjust brightness
    #
    # # Clip values to keep them within the valid range (0-255)
    # frame_hsv = np.clip(frame_hsv, 0, 255).astype(np.uint8)
    #
    # # Convert the frame back to BGR color space
    # frame_corrected = cv2.cvtColor(frame_hsv, cv2.COLOR_HSV2BGR)
    return frame

def findObjects(outputs, img):
    hT, wT, cT = img.shape
    bbox = []
    classIds = []
    confs = []
    detected_classes = []  # List to store the class names of detected objects

    for output in outputs:
        for det in output:
            scores = det[5:]
            classId = np.argmax(scores)
            confidence = scores[classId]
            if confidence > confThreshold:
                w, h = int(det[2] * wT), int(det[3] * hT)
                x, y = int((det[0] * wT) - w / 2), int((det[1] * hT) - h / 2)
                bbox.append([x, y, w, h])
                classIds.append(classId)
                confs.append(float(confidence))

    indices = cv2.dnn.NMSBoxes(bbox, confs, confThreshold, nmsThreshold)

    for i in indices:
        k = i  # Extract the index from the list
        box = bbox[k]
        x, y, w, h = box[0], box[1], box[2], box[3]
        class_name = classNames[classIds[k]].upper()
        detected_classes.append(class_name)
        dummy = "STOP SIGN"
        # Draw the rectangle and class name on the image
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 255), 2)
        cv2.putText(img, class_name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)

    return detected_classes


def perform_u_turn(drone,total_distance,path):
    # Rotate the drone clockwise by the specified angle
    #drone.rotate_clockwise(180)
    my_path = "a"
    if path == "a":
        cmd = 'EXT mled g 000rr000000rr000000rr000000rr000rrrrrrrr0rrrrrr000rrrr00000rr000'
        send_command(cmd)
        drone.move_back(30)
        time.sleep(1)
        drone.rotate_clockwise(90)
        total_distance = total_distance-30
        my_path = "b"
        return (total_distance,my_path)
    elif path == "b":
        cmd = 'EXT mled g 000rr000000rr000000rr000000rr000rrrrrrrr0rrrrrr000rrrr00000rr000'
        send_command(cmd)
        drone.move_back(60)
        drone.rotate_clockwise(-90)
        time.sleep(1)
        total_distance = total_distance - 60
        my_path = "c"
        return (total_distance, my_path)
    else:
        return (total_distance, my_path)
