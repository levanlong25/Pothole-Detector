import cv2
import os
import supervision as sv
from inference import get_model
from datetime import datetime

model = get_model(model_id="pothole-detection-yolov8/1", api_key="yNaUmMfXGJVNjP97wTcp")

OUTPUT_DIR = "save_potholes"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def detect_potholes(frame, save_result=True):
    global model
    
    results = model.infer(frame)[0]
    detections = sv.Detections.from_inference(results)

    for i, (box, conf) in enumerate(zip(detections.xyxy, detections.confidence)):
        x1, y1, x2, y2 = box
        print(f"Ổ gà {i+1}: Toạ độ = ({x1:.0f}, {y1:.0f}, {x2:.0f}, {y2:.0f}), Độ tin cậy = {conf:.2f}")

    if hasattr(model, 'class_names'):
        class_names_data = model.class_names
    else:
        class_names_data = ['pothole']

    labels = []
    for confidence, class_id in zip(detections.confidence, detections.class_id):
        idx = int(class_id)
        if isinstance(class_names_data, list):
            if idx < len(class_names_data):
                class_name = class_names_data[idx]
            else:
                class_name = 'pothole'
        elif isinstance(class_names_data, dict):
            class_name = class_names_data.get(idx, 'pothole')
        else:
            class_name = 'pothole'
        
        labels.append(f"{class_name} {confidence:.2f}")

    bounding_box_annotator = sv.BoxAnnotator()
    label_annotator = sv.LabelAnnotator()

    annotated_frame = bounding_box_annotator.annotate(scene=frame, detections=detections)
    annotated_frame = label_annotator.annotate(scene=annotated_frame, detections=detections, labels=labels)

    if save_result and len(detections) > 0:
        filename = f"pothole_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.jpg"
        filepath = os.path.join(OUTPUT_DIR, filename)
        cv2.imwrite(filepath, annotated_frame)
        print(f"Frame có ổ gà đã lưu: {filepath}")

    return annotated_frame