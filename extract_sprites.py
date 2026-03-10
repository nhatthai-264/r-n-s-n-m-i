import cv2
import numpy as np
import os

def extract_sprites(image_path, output_dir, min_area=10):
    """
    Trích xuất các sprites lẻ từ một sprite sheet có nền trong suốt.
    """
    if not os.path.exists(image_path):
        print(f"Lỗi: Không tìm thấy file {image_path}")
        return

    # Đọc ảnh với kênh alpha (trong suốt)
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    
    if img is None:
        print(f"Lỗi: Không thể đọc ảnh {image_path}")
        return

    # Kiểm tra xem ảnh có kênh alpha không (shape có 4 kênh phân lớp không)
    if img.shape[2] != 4:
        print("Lỗi: Ảnh không có kênh alpha (nền trong suốt). Vui lòng dùng ảnh đã xóa nền.")
        return

    # Lấy riêng kênh alpha để tìm các phần tử (sprites)
    alpha_channel = img[:, :, 3]

    # Phân ngưỡng: pixel có alpha > 10 sẽ thành 255 (trắng), còn lại thành 0 (đen)
    _, thresh = cv2.threshold(alpha_channel, 10, 255, cv2.THRESH_BINARY)

    # Tìm contours (đường viền bao xung quanh các sprites)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Tạo thư mục đầu ra nếu chưa có
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Tìm thấy {len(contours)} đối tượng tiềm năng.")

    sprite_count = 0
    # Sắp xếp contours từ trên xuống dưới, từ trái qua phải (hoặc chỉ lặp qua)
    # Lật ngược contours do OpenCV đôi khi lặp từ dưới lên
    contours = sorted(contours, key=lambda c: (cv2.boundingRect(c)[1], cv2.boundingRect(c)[0]))

    for contour in contours:
        # Bỏ qua các contours quá nhỏ (có thể là nhiễu rác)
        if cv2.contourArea(contour) < min_area:
            continue

        # Lấy bounding box (hình chữ nhật bao quanh contour)
        x, y, w, h = cv2.boundingRect(contour)

        # Cắt phần sprite từ ảnh gốc dựa trên tọa độ bounding box
        sprite = img[y:y+h, x:x+w]

        # Tên file cho sprite
        output_path = os.path.join(output_dir, f"sprite_{sprite_count:03d}.png")
        cv2.imwrite(output_path, sprite)
        sprite_count += 1

    print(f"Thành công! Đã trích xuất và lưu {sprite_count} sprites vào thư mục '{output_dir}'.")

if __name__ == "__main__":
    # Sử dụng ảnh sheet đã được xóa nền
    input_sheet = "sprites_sheet-removebg-preview.png"
    output_folder = "sprites"
    
    print(f"Đang xử lý {input_sheet} ...")
    extract_sprites(input_sheet, output_folder)
