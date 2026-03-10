import cv2
import numpy as np
import os

def remove_background(input_path, output_path, tolerance=10):
    """
    Xóa nền cho ảnh bằng OpenCV dựa trên màu nền ở góc trên bên trái.
    """
    if not os.path.exists(input_path):
        print(f"Lỗi: Không tìm thấy file {input_path}")
        return False

    # Đọc ảnh (bao gồm cả kênh alpha nếu có)
    img = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
    
    if img is None:
        print(f"Lỗi: Không thể đọc file {input_path}")
        return False

    # Chuyển ảnh sang dạng BGRA nếu chưa có kênh Alpha (độ trong suốt)
    if img.shape[2] == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)

    # Lấy màu nền từ vị trí trên cùng bên trái (Top-Left)
    bg_color = img[0, 0]
    b, g, r = int(bg_color[0]), int(bg_color[1]), int(bg_color[2])

    print(f"Màu nền phát hiện được (BGR): {b}, {g}, {r}")

    # Tạo giới hạn khoảng màu cho nền (để xử lý nhiễu nhỏ trong màu nền nếu có)
    lower_bound = np.array([max(0, b - tolerance), max(0, g - tolerance), max(0, r - tolerance), 0])
    upper_bound = np.array([min(255, b + tolerance), min(255, g + tolerance), min(255, r + tolerance), 255])

    # Tạo Mask để xác định khu vực có màu nền
    mask = cv2.inRange(img, lower_bound, upper_bound)

    # Đổi thuộc tính Alpha (kênh thứ 4) của các pixel nền thành 0 (trong suốt)
    img[mask == 255, 3] = 0

    # Lưu kết quả
    cv2.imwrite(output_path, img)
    print(f"Thành công! Đã lưu ảnh không nền tại: {output_path}")
    return True

if __name__ == "__main__":
    input_file = "sprites_sheet.png"
    output_file = "sprites_sheet_transparent.png"
    
    print(f"Đang xử lý {input_file} ...")
    remove_background(input_file, output_file)
