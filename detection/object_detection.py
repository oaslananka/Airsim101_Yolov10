# detection/object_detection.py
import airsim
import numpy as np
import cv2
from ultralytics import YOLO
from utils.robust_image import get_image_safe

model = YOLO("yolov10n.pt")

def yolov10_object_detection(client) -> bool:
    """
    Perform object detection using YOLOv10 model with robust image retrieval.

    Args:
        client: The AirSim client object.

    Returns:
        bool: True if the detection is successful, False otherwise.
    """
    # Use robust image retrieval instead of direct simGetImage call
    img = get_image_safe(client, camera="0", retries=3, sleep=0.2, compress=True)
    
    if img is None:
        return True  # Continue operation even if image retrieval fails
    
    if img.shape[2] == 4:
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    results = model(img)

    for box in results[0].boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
        label = model.names[int(box.cls[0].cpu().numpy())]
        confidence = box.conf[0].cpu().numpy()
        
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(img, f"{label} {confidence:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    cv2.imshow("Top", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        return False
    return True
