import cv2
import tkinter as tk
from tkinter import filedialog, Label, Button
from PIL import Image, ImageTk
import os
import detect_potholes as dp

BG_COLOR = "#3CA1D7"          
PRIMARY_COLOR = "#0078d7"    
PRIMARY_HOVER = "#005a9e"     
SECONDARY_COLOR = "#6c757d"  
SECONDARY_HOVER = "#5a6268"   
DANGER_COLOR = "#e81123"      
DANGER_HOVER = "#c50f1f"     
TEXT_COLOR = "#EF0505"        
SUBTEXT_COLOR = "#FB0000"    
SAVED_IMAGES_DIR = "save_potholes"  

root = tk.Tk()
root.title("Ứng dụng phát hiện ổ gà")
root.geometry("1000x750")           
root.resizable(True, True)          
root.configure(bg=BG_COLOR)

cap = None  

title_label = Label(
    root,
    text="Ứng dụng phát hiện ổ gà",
    font=("Segoe UI", 32, "bold"),
    bg=BG_COLOR,
    fg=TEXT_COLOR,
)
title_label.pack(pady=(25, 5))

description_label = Label(
    root,
    text="Nâng cao an toàn giao thông với hệ thống phát hiện ổ gà",
    font=("Segoe UI", 14),
    bg=BG_COLOR,
    fg=SUBTEXT_COLOR,
)
description_label.pack(pady=(0, 25))

# ======================
# 🧭 KHUNG CHỨA CÁC NÚT CHỨC NĂNG CHÍNH
# ======================
button_frame = tk.Frame(root, bg=BG_COLOR)
button_frame.pack(pady=(0, 25))

def style_button(btn, bg, fg, hover_bg, width=20, height=2):
    """Định dạng style hiện đại cho các nút (màu, font, hiệu ứng hover)"""
    btn.config(
        font=("Segoe UI", 14, "bold"),
        bg=bg,
        fg=fg,
        activebackground=hover_bg,
        activeforeground=fg,
        width=width,
        height=height,
        bd=0,
        relief="flat",
        highlightthickness=0,
        cursor="hand2",
    )
    # Hiệu ứng đổi màu khi di chuột vào/ra
    btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg))

# ======================
# ⚙️ CÁC HÀM TIỆN ÍCH CHO ỨNG DỤNG
# ======================
def reset_ui():
    """Đưa giao diện về trạng thái ban đầu"""
    image_button.pack(side="left", padx=10)
    video_button.pack(side="left", padx=10)
    view_button.pack(side="left", padx=10)
    close_button.pack_forget()
    empty_label.config(image="", text="Chọn một phương thức ở trên để bắt đầu.")

def resize_image(image, target_height):
    """Hàm resize ảnh hoặc frame video theo chiều cao, giữ nguyên tỉ lệ"""
    (h, w) = image.shape[:2]
    aspect_ratio = w / h
    new_width = int(target_height * aspect_ratio)
    return cv2.resize(image, (new_width, target_height))

# ======================
# 📸 CHỨC NĂNG PHÁT HIỆN Ổ GÀ TRÊN ẢNH
# ======================
def detect_from_image():
    """Xử lý phát hiện ổ gà từ ảnh tĩnh"""
    hide_initial_buttons()
    file_path = filedialog.askopenfilename(filetypes=[("Ảnh", "*.jpg *.png *.jpeg")])
    if file_path:
        # Đọc ảnh và đưa vào module detect_potholes
        image = cv2.imread(file_path)
        detected_image = dp.detect_potholes(image)
        # Resize ảnh hiển thị cho phù hợp với giao diện
        resized_image = resize_image(detected_image, 475)
        img = cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        imgtk = ImageTk.PhotoImage(image=img)
        # Hiển thị ảnh kết quả lên giao diện
        empty_label.imgtk = imgtk
        empty_label.configure(image=imgtk)
    else:
        reset_ui()

# ======================
# 🎥 CHỨC NĂNG PHÁT HIỆN Ổ GÀ TRÊN VIDEO
# ======================
def detect_from_video():
    """Xử lý phát hiện ổ gà từ video (chạy frame-by-frame)"""
    global cap
    hide_initial_buttons()
    file_path = filedialog.askopenfilename(filetypes=[("Video", "*.mp4 *.avi")])
    if file_path:
        cap = cv2.VideoCapture(file_path)
        video_loop(cap)
    else:
        reset_ui()

def video_loop(capture):
    """Đọc từng frame của video và phát hiện liên tục"""
    if not cap:
        return  # Dừng nếu người dùng đã dừng phát hiện
    ret, frame = capture.read()
    if ret:
        detected_frame = dp.detect_potholes(frame)  # Gọi model YOLOv8 phát hiện
        resized_frame = resize_image(detected_frame, 600)
        img = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        imgtk = ImageTk.PhotoImage(image=img)
        empty_label.imgtk = imgtk
        empty_label.configure(image=imgtk)
        # Lặp lại sau 10ms để xử lý frame tiếp theo
        empty_label.after(10, lambda: video_loop(capture))
    else:
        capture.release()
        stop_detection()

# ======================
# 🛑 DỪNG PHÁT HIỆN
# ======================
def stop_detection():
    """Giải phóng video capture và đưa giao diện về trạng thái ban đầu"""
    global cap
    if cap:
        cap.release()
        cap = None
    reset_ui()

def hide_initial_buttons():
    """Ẩn các nút ban đầu, chỉ hiện nút 'Dừng phát hiện' khi đang chạy"""
    image_button.pack_forget()
    video_button.pack_forget()
    view_button.pack_forget()
    close_button.pack(side="left", padx=10)

# ======================
# 🖼️ CHỨC NĂNG XEM ẢNH ĐÃ LƯU (GALLERY)
# ======================
def show_saved_images():
    """Hiển thị thư viện ảnh đã lưu (giao diện đẹp, gọn gàng, chỉ mở 1 lần)"""
    # Nếu cửa sổ gallery đã mở -> đưa lên trên cùng, không mở thêm
    if hasattr(root, "gallery_window") and root.gallery_window.winfo_exists():
        root.gallery_window.lift()
        return

    gallery_window = tk.Toplevel(root)
    root.gallery_window = gallery_window
    gallery_window.title("📸 Thư viện ảnh ổ gà đã phát hiện")
    gallery_window.geometry("950x650")
    gallery_window.configure(bg="#f8f9fa")
    gallery_window.resizable(False, False)

    # Lưu danh sách ảnh đã mở chi tiết
    gallery_window.opened_details = {}
    gallery_window.thumbnails = []

    # Tiêu đề gallery
    title = Label(
        gallery_window,
        text="Thư viện ảnh ổ gà đã lưu",
        font=("Segoe UI", 20, "bold"),
        fg="#212529",
        bg="#f8f9fa"
    )
    title.pack(pady=(15, 10))

    # Khung chứa canvas có thanh cuộn
    main_frame = tk.Frame(gallery_window, bg="#f8f9fa")
    main_frame.pack(fill=tk.BOTH, expand=1, padx=20, pady=(0, 20))

    canvas = tk.Canvas(main_frame, bg="#f8f9fa", highlightthickness=0)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

    scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.configure(yscrollcommand=scrollbar.set)

    image_frame = tk.Frame(canvas, bg="#f8f9fa")
    canvas.create_window((0, 0), window=image_frame, anchor="nw")

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    image_frame.bind("<Configure>", on_frame_configure)

    # Kiểm tra thư mục tồn tại
    if not os.path.isdir(SAVED_IMAGES_DIR):
        Label(
            image_frame,
            text=f"❌ Thư mục '{SAVED_IMAGES_DIR}' không tồn tại.\nHãy chạy phát hiện để lưu ảnh vào đây.",
            font=("Segoe UI", 14),
            bg="#f8f9fa",
            fg="#dc3545",
        ).pack(pady=30)
        return

    image_files = [
        f for f in os.listdir(SAVED_IMAGES_DIR)
        if f.lower().endswith(('.png', '.jpg', '.jpeg'))
    ]

    if not image_files:
        Label(
            image_frame,
            text="Không có ảnh nào để hiển thị.",
            font=("Segoe UI", 14),
            bg="#f8f9fa",
            fg="#6c757d",
        ).pack(pady=30)
        return

    # Hàm mở chi tiết ảnh (1 ảnh 1 cửa sổ duy nhất)
    def open_image_detail(image_path):
        if image_path in gallery_window.opened_details:
            win = gallery_window.opened_details[image_path]
            if win.winfo_exists():
                win.lift()
                return

        win = tk.Toplevel(gallery_window)
        win.title(os.path.basename(image_path))
        win.configure(bg="#f8f9fa")

        def on_close():
            if image_path in gallery_window.opened_details:
                del gallery_window.opened_details[image_path]
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", on_close)

        img = Image.open(image_path)
        screen_w, screen_h = win.winfo_screenwidth(), win.winfo_screenheight()
        img.thumbnail((screen_w - 100, screen_h - 150))
        photo = ImageTk.PhotoImage(img)
        lbl = Label(win, image=photo, bg="#f8f9fa")
        lbl.image = photo
        lbl.pack(padx=10, pady=10)

        gallery_window.opened_details[image_path] = win

    # Hiển thị danh sách ảnh dạng lưới
    row, col = 0, 0
    max_cols = 3

    for img_file in sorted(image_files, reverse=True):
        img_path = os.path.join(SAVED_IMAGES_DIR, img_file)
        try:
            img = Image.open(img_path)
            img.thumbnail((250, 250))
            photo = ImageTk.PhotoImage(img)
            gallery_window.thumbnails.append(photo)

            # 👉 Tạo khung cho mỗi ảnh (viền, bo góc, bóng đổ)
            frame = tk.Frame(
                image_frame,
                bg="white",
                bd=0,
                highlightthickness=0,
            ) 
            frame.grid(row=row, column=col, padx=20, pady=20)
            frame.grid_propagate(False)
            frame.configure(width=260, height=260)

            # 👉 Ảnh thu nhỏ trong khung
            lbl = Label(frame, image=photo, bg="white", cursor="hand2")
            lbl.image = photo
            lbl.place(relx=0.5, rely=0.5, anchor="center")  

            # Hiệu ứng hover (ảnh sáng lên nhẹ)
            def on_enter(e, l=lbl): l.config(bg="#f1f3f5")
            def on_leave(e, l=lbl): l.config(bg="white")
            lbl.bind("<Enter>", on_enter)
            lbl.bind("<Leave>", on_leave)

            # Nhấn vào ảnh => mở chi tiết
            lbl.bind("<Button-1>", lambda e, path=img_path: open_image_detail(path))

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

        except Exception as e:
            print(f"Lỗi khi tải ảnh {img_path}: {e}")

# ======================
# 🔘 TẠO CÁC NÚT CHỨC NĂNG
# ======================
image_button = Button(button_frame, text="Bắt đầu với ảnh", command=detect_from_image)
video_button = Button(button_frame, text="Bắt đầu với video", command=detect_from_video)
view_button = Button(button_frame, text="Xem ảnh đã lưu", command=show_saved_images)
close_button = Button(button_frame, text="Dừng phát hiện", command=stop_detection)

# Áp dụng style cho từng nút
style_button(image_button, PRIMARY_COLOR, "white", PRIMARY_HOVER)
style_button(video_button, PRIMARY_COLOR, "white", PRIMARY_HOVER)
style_button(view_button, SECONDARY_COLOR, "white", SECONDARY_HOVER)
style_button(close_button, DANGER_COLOR, "white", DANGER_HOVER)

# ======================
# 🖥️ KHUNG HIỂN THỊ ẢNH / VIDEO TRÊN GIAO DIỆN CHÍNH
# ======================
preview_frame = tk.Frame(
    root,
    width=750,
    height=650,
    bg="white",
    borderwidth=0,
    highlightthickness=2,
    highlightbackground="#cccccc",
)
preview_frame.pack_propagate(False)
preview_frame.pack(pady=(10, 25))

# Label trống mặc định khi chưa có ảnh/video
empty_label = Label(
    preview_frame,
    bg="white",
    fg="#999999",
    font=("Segoe UI", 14, "italic"),
    text="📷 Chọn một phương thức ở trên để bắt đầu.",
)
empty_label.place(relx=0.5, rely=0.5, anchor="center")

# ======================
# 📄 PHẦN CHÂN TRANG (FOOTER)
# ======================
footer_label = Label(
    root,
    text="© 2025 - Demo AI Project - Nhóm nghiên cứu ATGT",
    font=("Segoe UI", 10),
    bg=BG_COLOR,
    fg="#888888",
)
footer_label.pack(side="bottom", pady=10)

# ======================
# 🚀 KHỞI CHẠY ỨNG DỤNG
# ======================
reset_ui()
root.mainloop()
