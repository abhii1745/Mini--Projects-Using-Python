import cv2
import cvzone
from cvzone.SelfiSegmentationModule import SelfiSegmentation
import time
import os


cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(3, 640)  # width
cap.set(4, 480)  # height


segmentor = SelfiSegmentation()


background_images = []
for i in range(1, 4):  
    img_path = f"bg{i}.jpg"
    if os.path.exists(img_path):
        bg_img = cv2.imread(img_path)
        if bg_img is not None:
            background_images.append(bg_img)
        else:
            print(f"Warning: {img_path} could not be loaded as an image.")
    else:
        print(f"Warning: {img_path} not found.")

if not background_images:
    raise ValueError("No background images found. Please check the file paths.")

current_bg_index = 0


fps_start_time = time.time()
fps_counter = 0

while True:
    success, img = cap.read()
    if not success:
        break

  
    bg_img = background_images[current_bg_index]
    if img.shape[:2] != bg_img.shape[:2]:
        bg_img = cv2.resize(bg_img, (img.shape[1], img.shape[0]))

 
    imgout = segmentor.removeBG(img, bg_img)

    
    fps_counter += 1
    if time.time() - fps_start_time >= 1:
        fps = fps_counter
        fps_counter = 0
        fps_start_time = time.time()
        fps_text = f"FPS: {fps}"
    else:
        fps_text = f"FPS: {fps_counter}"

   
    try:
        imgstacked = cvzone.stackImages([img, imgout], 2, 1)
    except Exception as e:
        print(f"Error stacking images: {e}")
        break

    cv2.putText(imgstacked, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    
    cv2.imshow("image", imgstacked)

    
    key = cv2.waitKey(10)
    if key == ord('q'):
        break
    elif key == ord('n'):  
        current_bg_index = (current_bg_index + 1) % len(background_images) 
    elif key == ord('p'):  
        current_bg_index = (current_bg_index - 1) % len(background_images)  


cv2.destroyAllWindows()
cap.release()
