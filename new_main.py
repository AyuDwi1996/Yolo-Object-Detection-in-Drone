from utils import *
total_distance = 0
whT = 320
confThreshold = 0.5
nmsThreshold = 0.3
classesFile = 'coco.names'
classNames = []
path = "a"
with open(classesFile, 'rt') as f:
    classNames = f.read().rstrip('\n').split('\n')

modelConfiguration = 'yolov3.cfg'
modelWeights = 'yolov3.weights'

net = cv2.dnn.readNetFromDarknet(modelConfiguration, modelWeights)
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
startCounter = 0
myDrone = intializeTello()
time.sleep(5)
#flag_first_time = True
while True:
    if cv2.waitKey(1) and 0xFF == ord('q'):
        # replace the 'and' with '&amp;'
        myDrone.land()
        break

    #Flight
    if startCounter == 0:
        img = telloGetFrame(myDrone)
        #myDrone.takeoff()
        # time.sleep(3)
        # myDrone.move_down(30)
        # time.sleep(3)
        # #time.sleep(1)
        # myDrone.move_up(30)
        # time.sleep(3)
        #img = telloGetFrame(myDrone)
        #cv2.imshow("Tello Video", img)
        #time.sleep(3)
        #myDrone.move_down(30)
        startCounter = 1
    # STEP 1
    img = telloGetFrame(myDrone)
    #cv2.imshow("Tello Video", img)
    # STEP 2
    blob = cv2.dnn.blobFromImage(img, 1 / 255, (whT, whT), [0, 0, 0], 1, crop=False)
    net.setInput(blob)
    layerNames = net.getLayerNames()
    outputIndices = net.getUnconnectedOutLayers()
    outputNames = [layerNames[i - 1] for i in outputIndices]
    outputs = net.forward(outputNames)
    detected_obj=findObjects(outputs, img)
    cv2.imshow("Tello Video", img)
    print(detected_obj)
    if "UMBRELLA" in detected_obj:
        strcmd = 'EXT mled g'
        strcmd = strcmd + " " + "00pppp000pppppp0pppppppppppppppp0000p0000000p00000p0p00000ppp000"
        send_command(strcmd)
        time.sleep(3)
    if "TEDDY BEAR" in detected_obj:
        send_command('EXT mled s r heart')
        time.sleep(3)

    if "WINE GLASS" in detected_obj:
        strcmd = 'EXT mled g'
        strcmd = strcmd + " " + "bbbbbbbbbbbbbbbbbbbbbbbb0bbbbbb0000bb000000bb000000bb000bbbbbbbb"
        send_command(strcmd)
        time.sleep(3)




