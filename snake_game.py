import pygame
import sys
import random
import cv2
import mediapipe as mp
import numpy as np
import threading
import time

# Khởi tạo Pygame
pygame.init()

# Khởi tạo MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mp_draw = mp.solutions.drawing_utils

# Khởi tạo Camera
cap = cv2.VideoCapture(0)

# Kích thước màn hình
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# Màu sắc (pixel đen trắng)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Kích thước khối cờ (pixel)
BLOCK_SIZE = 20

# Tốc độ game
FPS = 5

# Shared variables for Camera Thread
current_frame = None
latest_gesture = None  # Cử chỉ phát hiện được ("UP", "DOWN", "LEFT", "RIGHT")
camera_active = True

def gesture_processing_thread():
    global current_frame, latest_gesture, camera_active
    
    prev_x, prev_y = 0, 0
    swipe_threshold = 25 # Minimum pixel movement to count as a swipe
    cooldown = 0
    
    while camera_active:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.1)
            continue
            
        frame = cv2.flip(frame, 1) # Mirror image
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)
        
        h, w, c = frame.shape
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                # Use tip of index finger (landmark 8) for tracking
                cx, cy = int(hand_landmarks.landmark[8].x * w), int(hand_landmarks.landmark[8].y * h)
                
                if cooldown > 0:
                    cooldown -= 1
                else:
                    if prev_x != 0 and prev_y != 0:
                        dx = cx - prev_x
                        dy = cy - prev_y
                        
                        # Determine swipe direction
                        if abs(dx) > swipe_threshold or abs(dy) > swipe_threshold:
                            if abs(dx) > abs(dy):
                                if dx > 0: # Swipe Right
                                    latest_gesture = "RIGHT"
                                    cooldown = 15
                                elif dx < 0: # Swipe Left
                                    latest_gesture = "LEFT"
                                    cooldown = 15
                            else:
                                if dy > 0: # Swipe Down
                                    latest_gesture = "DOWN"
                                    cooldown = 15
                                elif dy < 0: # Swipe Up
                                    latest_gesture = "UP"
                                    cooldown = 15
                                    
                # Draw tracking point
                cv2.circle(frame, (cx, cy), 15, (0, 255, 0), -1)
                prev_x, prev_y = cx, cy
        else:
            prev_x, prev_y = 0, 0
            
        current_frame = frame
        time.sleep(0.01) # Small sleep to prevent 100% CPU lock

# Khởi chạy thread xử lý camera
cam_thread = threading.Thread(target=gesture_processing_thread, daemon=True)
cam_thread.start()

# Khởi tạo màn hình
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Snake - Black & White Pixel Art")

clock = pygame.time.Clock()

try:
    font_style = pygame.font.SysFont("courier", 24, bold=True)
    large_font = pygame.font.SysFont("courier", 36, bold=True)
except:
    font_style = pygame.font.Font(None, 24)
    large_font = pygame.font.Font(None, 36)

def draw_score(score):
    value = font_style.render(f"Score: {score}", True, WHITE)
    screen.blit(value, [10, 10])

def draw_snake(snake_list):
    for block in snake_list:
        pygame.draw.rect(screen, WHITE, [block[0], block[1], BLOCK_SIZE, BLOCK_SIZE])

def get_random_food_pos(exclude_list, size=BLOCK_SIZE):
    while True:
        x = round(random.randrange(0, WINDOW_WIDTH - size) / BLOCK_SIZE) * BLOCK_SIZE
        y = round(random.randrange(0, WINDOW_HEIGHT - size) / BLOCK_SIZE) * BLOCK_SIZE
        
        # Đảm bảo mồi mới không nằm đè lên thân rắn
        collision = False
        for block in exclude_list:
            if (block[0] >= x and block[0] < x + size) and (block[1] >= y and block[1] < y + size):
                collision = True
                break
        
        if not collision:
            return x, y

def game_loop():
    global latest_gesture
    game_over = False
    game_close = False
    
    # Consume any pending gesture at game start
    latest_gesture = None

    # Vị trí đầu rắn ban đầu
    x1 = WINDOW_WIDTH // 2
    y1 = WINDOW_HEIGHT // 2

    x1_change = BLOCK_SIZE
    y1_change = 0

    snake_list = []
    snake_length = 3
    
    # Khởi tạo rắn ban đầu (nằm ngang)
    for i in range(snake_length):
        snake_list.append([x1 - i * BLOCK_SIZE, y1])

    score = 0
    small_food_eaten = 0

    # Khởi tạo vị trí mồi nhỏ
    food_x, food_y = get_random_food_pos(snake_list)

    # Khởi tạo biến cho mồi lớn
    big_food_active = False
    big_food_x, big_food_y = -100, -100
    big_food_size = BLOCK_SIZE * 2

    while not game_over:
        while game_close:
            screen.fill(BLACK)
            go_msg = large_font.render("GAME OVER", True, WHITE)
            restart_msg = font_style.render("Restarting...", True, WHITE)
            score_msg = font_style.render(f"Final Score: {score}", True, WHITE)
            
            screen.blit(go_msg, [WINDOW_WIDTH // 2 - go_msg.get_width() // 2, WINDOW_HEIGHT // 3])
            screen.blit(restart_msg, [WINDOW_WIDTH // 2 - restart_msg.get_width() // 2, WINDOW_HEIGHT // 2])
            screen.blit(score_msg, [WINDOW_WIDTH // 2 - score_msg.get_width() // 2, WINDOW_HEIGHT // 2 + 50])
            
            pygame.display.update()
            
            # Wait for 2 seconds then restart automatically
            pygame.time.delay(2000)
            return  # Trả về để được gọi lại bởi hàm main
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and x1_change == 0:
                    x1_change = -BLOCK_SIZE
                    y1_change = 0
                elif event.key == pygame.K_RIGHT and x1_change == 0:
                    x1_change = BLOCK_SIZE
                    y1_change = 0
                elif event.key == pygame.K_UP and y1_change == 0:
                    y1_change = -BLOCK_SIZE
                    x1_change = 0
                elif event.key == pygame.K_DOWN and y1_change == 0:
                    y1_change = BLOCK_SIZE
                    x1_change = 0

        # --- Áp dụng Gesture nhận được từ Thread Camera ---
        if latest_gesture == "LEFT" and x1_change == 0:
            x1_change = -BLOCK_SIZE
            y1_change = 0
        elif latest_gesture == "RIGHT" and x1_change == 0:
            x1_change = BLOCK_SIZE
            y1_change = 0
        elif latest_gesture == "UP" and y1_change == 0:
            y1_change = -BLOCK_SIZE
            x1_change = 0
        elif latest_gesture == "DOWN" and y1_change == 0:
            y1_change = BLOCK_SIZE
            x1_change = 0
            
        # Clear gesture queue sau khi đã xử lý trong frame này
        latest_gesture = None

        # Cập nhật vị trí đầu rắn
        x1 += x1_change
        y1 += y1_change

        # Kiểm tra đụng tường
        if x1 >= WINDOW_WIDTH or x1 < 0 or y1 >= WINDOW_HEIGHT or y1 < 0:
            game_close = True

        screen.fill(BLACK)
        
        # Vẽ mồi nhỏ
        pygame.draw.rect(screen, WHITE, [food_x, food_y, BLOCK_SIZE, BLOCK_SIZE])
        
        # Vẽ mồi lớn (nếu có)
        if big_food_active:
            pygame.draw.rect(screen, WHITE, [big_food_x, big_food_y, big_food_size, big_food_size])

        # Cập nhật mảng thân rắn
        snake_head = [x1, y1]
        snake_list.append(snake_head)
        
        if len(snake_list) > snake_length:
            del snake_list[0]

        # Kiểm tra rắn cắn vào đuôi
        for block in snake_list[:-1]:
            if block == snake_head:
                game_close = True

        # Vẽ rắn
        draw_snake(snake_list)
        # Hiển thị điểm số
        draw_score(score)

        # Draw camera feed (Picture-in-Picture)
        if current_frame is not None:
            # Resize frame for PiP (Tăng kích thước lên gấp đôi để dễ nhìn tay)
            pip_w, pip_h = 320, 240
            pip_frame = cv2.resize(current_frame, (pip_w, pip_h))
            pip_frame = cv2.cvtColor(pip_frame, cv2.COLOR_BGR2RGB)
            
            # Convert to Pygame surface
            # Pygame shape requirement: (width, height, channels)
            # OpenCV provides (height, width, channels)
            pip_surface = pygame.surfarray.make_surface(np.rot90(pip_frame))
            pip_surface = pygame.transform.flip(pip_surface, True, False)
            
            # Draw a border around PIP
            pygame.draw.rect(pip_surface, (0, 255, 0), pip_surface.get_rect(), 3)
            
            # Blit onto main screen (top right corner)
            screen.blit(pip_surface, (WINDOW_WIDTH - pip_w - 10, 10))

        pygame.display.update()

        # Xử lý ăn mồi nhỏ
        if x1 == food_x and y1 == food_y:
            food_x, food_y = get_random_food_pos(snake_list)
            snake_length += 1
            score += 1
            small_food_eaten += 1
            
            # Kích hoạt mồi lớn mỗi khi đủ 10 mồi nhỏ
            if small_food_eaten >= 10:
                small_food_eaten = 0
                if not big_food_active:
                    big_food_active = True
                    big_food_x, big_food_y = get_random_food_pos(snake_list, size=big_food_size)

        # Xử lý ăn mồi lớn
        if big_food_active:
            # Kiểm tra xem rắn có ăn trúng phần diện tích 4 blocks của khối mồi lớn 2x2 không
            if (big_food_x <= x1 < big_food_x + big_food_size) and \
               (big_food_y <= y1 < big_food_y + big_food_size):
                score += 5
                snake_length += 2 # Tùy chọn: Tăng chiều dài nhiều hơn khi ăn mồi lớn
                big_food_active = False # Biến mất mồi lớn sau khi ăn

        clock.tick(FPS)

def main():
    global camera_active
    try:
        while True:
            game_loop()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        camera_active = False # Signal camera thread to exit
        pygame.quit()
        if cap.isOpened():
            cap.release()
        sys.exit()

if __name__ == '__main__':
    main()
