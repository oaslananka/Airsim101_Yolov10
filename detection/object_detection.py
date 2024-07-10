# detection/object_detection.py
import airsim
import numpy as np
import cv2
from ultralytics import YOLO

model = YOLO("yolov10n.pt")

def yolov10_object_detection(client) -> bool:
    """
    Perform object detection using YOLOv10 model.

    Args:
        client: The AirSim client object.

    Returns:
        bool: True if the detection is successful, False otherwise.
    """
    result = client.simGetImage("FrontCenter", airsim.ImageType.Scene)
    raw_image = np.frombuffer(result, np.int8)
    img = cv2.imdecode(raw_image, cv2.IMREAD_UNCHANGED)
    
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
