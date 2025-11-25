import cv2
import os
import supervision as sv
from inference import get_model
from datetime import datetime

# ======================
# ⚙️ KHỞI TẠO MÔ HÌNH YOLOv8
# ======================

# Gọi model đã huấn luyện sẵn trên nền tảng Roboflow
# "pothole-detection-yolov8/1" là ID của model đã được train để nhận diện ổ gà
# api_key là khóa để xác thực khi gọi model qua thư viện inference
model = get_model(model_id="pothole-detection-yolov8/1", api_key="yNaUmMfXGJVNjP97wTcp")

# ======================
# 🗂️ CẤU HÌNH THƯ MỤC LƯU ẢNH KẾT QUẢ
# ======================
OUTPUT_DIR = "save_potholes"  # Tên thư mục lưu frame có phát hiện ổ gà

# Nếu thư mục chưa tồn tại → tự động tạo mới
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# ======================
# 🚗 HÀM CHÍNH: PHÁT HIỆN Ổ GÀ TRÊN MỘT FRAME
# ======================
def detect_potholes(frame, save_result=True):
    """
    Hàm phát hiện ổ gà trong 1 frame ảnh hoặc video.

    Tham số:
        frame (ndarray): khung hình đầu vào (ảnh đọc từ cv2 hoặc frame video)
        save_result (bool): nếu True → tự động lưu frame khi có phát hiện

    Trả về:
        annotated_frame (ndarray): ảnh đầu ra có vẽ bounding box và nhãn
    """

    # ======================
    # 🧠 1. Suy luận (Inference) bằng YOLOv8
    # ======================
    results = model.infer(frame)[0]  # Trả về danh sách kết quả phát hiện
    # Chuyển kết quả inference sang đối tượng Detections của thư viện supervision
    detections = sv.Detections.from_inference(results)
    # In ra tất cả toạ độ và confidence
    for i, (box, conf) in enumerate(zip(detections.xyxy, detections.confidence)):
        x1, y1, x2, y2 = box
        print(f"Ổ gà {i+1}: Toạ độ = ({x1:.0f}, {y1:.0f}, {x2:.0f}, {y2:.0f}),  Độ tin cậy = {conf:.2f}")

    # ======================
    # 🖍️ 2. TẠO ĐỐI TƯỢNG VẼ KHUNG & NHÃN
    # ======================
    bounding_box_annotator = sv.BoxAnnotator()    # Dùng để vẽ bounding box
    label_annotator = sv.LabelAnnotator()         # Dùng để ghi nhãn (label)

    # ======================
    # 🖼️ 3. VẼ KHUNG VÀ GHI NHÃN LÊN FRAME
    # ======================
    annotated_frame = bounding_box_annotator.annotate(scene=frame, detections=detections)
    annotated_frame = label_annotator.annotate(scene=annotated_frame, detections=detections)

    # ======================
    # 💾 4. NẾU PHÁT HIỆN Ổ GÀ → LƯU FRAME LẠI
    # ======================
    if save_result and len(detections) > 0:
        # Tạo tên file theo thời gian (đảm bảo không trùng)
        filename = f"pothole_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.jpg"
        filepath = os.path.join(OUTPUT_DIR, filename)

        # Ghi ảnh có khung và nhãn xuống thư mục kết quả
        cv2.imwrite(filepath, annotated_frame)
        print(f"Frame có ổ gà đã lưu: {filepath}")

    # ======================
    # 🔁 5. TRẢ KẾT QUẢ ĐÃ VẼ VỀ CHO ỨNG DỤNG
    # ======================
    return annotated_frame
