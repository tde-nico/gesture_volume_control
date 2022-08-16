import math
import time
import numpy as np
import cv2

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

import Hand_Tracking_Module as htm

WCAM, HCAM = 640, 480

cap = cv2.VideoCapture(0) # 1 ?
cap.set(3, WCAM)
cap.set(4, HCAM)

pTime = 0

detector = htm.HandDetector(detection_con=0.7)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
	IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

volume_range = volume.GetVolumeRange()
min_vol = volume_range[0]
max_vol = volume_range[1]
vol = 0
vol_bar = int(HCAM / 1.2)


while 1:
	success, img = cap.read()
	img = detector.find_hands(img)
	lm_list = detector.find_position(img, draw=False)
	if lm_list:
		x1, y1 = lm_list[4][1], lm_list[4][2]
		x2, y2 = lm_list[8][1], lm_list[8][2]
		cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
		cv2.circle(img, (x1,y1), 15, (255,0,255), cv2.FILLED)
		cv2.circle(img, (x2,y2), 15, (255,0,255), cv2.FILLED)
		cv2.line(img, (x1,y1), (x2,y2), (255,0,0), 3)
		length = math.hypot(x2 - x1, y2 - y1)

		vol = np.interp(length, [50,150], [min_vol, max_vol])
		volume.SetMasterVolumeLevel(vol,None)
		vol_bar = np.interp(length, [50,150], [int(HCAM/1.2), int(HCAM/3.2)])

	cv2.rectangle(img, (50,150), (85,400), (0,255,0), 3)
	cv2.rectangle(img, (50,int(vol_bar)), (85,400), (0,255,0), cv2.FILLED)

	cTime = time.time()
	fps = 1/(cTime - pTime)
	pTime = cTime

	cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
	cv2.imshow("Image", img)
	cv2.waitKey(1)
