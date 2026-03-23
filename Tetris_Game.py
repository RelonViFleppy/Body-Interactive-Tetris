import pygame
import random
import time
import cv2 
import numpy as np 

# --- 1. Constants Definitions ---

S_WIDTH = 800
S_HEIGHT = 700
PLAY_WIDTH = 300 
PLAY_HEIGHT = 600 
BLOCK_SIZE = 30 
TOP_LEFT_X = (S_WIDTH - PLAY_WIDTH) // 2
TOP_LEFT_Y = S_HEIGHT - PLAY_HEIGHT - 50

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (255, 0, 0)

S = [['.....', '.....', '..00.', '.00..', '.....'], ['.....', '..0..', '..00.', '...0.', '.....']]
Z = [['.....', '.....', '.00..', '..00.', '.....'], ['.....', '..0..', '.00..', '.0...', '.....']]
I = [['..0..', '..0..', '..0..', '..0..', '.....'], ['.....', '0000.', '.....', '.....', '.....']]
O = [['.....', '.....', '.00..', '.00..', '.....']]
J = [['.....', '.0...', '.000.', '.....', '.....'], ['.....', '..00.', '..0..', '..0..', '.....'], ['.....', '.....', '.000.', '...0.', '.....'], ['.....', '..0..', '..0..', '.00..', '.....']]
L = [['.....', '...0.', '.000.', '.....', '.....'], ['.....', '..0..', '..0..', '..00.', '.....'], ['.....', '.....', '.000.', '.0...', '.....'], ['.....', '.00..', '..0..', '..0..', '.....']]
T = [['.....', '..0..', '.000.', '.....', '.....'], ['.....', '..0..', '..00.', '..0..', '.....'], ['.....', '.....', '.000.', '..0..', '.....'], ['.....', '..0..', '.00..', '..0..', '.....']]

shapes = [S, Z, I, O, J, L, T]
shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (0, 0, 255), (255, 165, 0), (128, 0, 128)]

# --- 2. Helper Classes and Functions (Unchanged) ---

class Piece(object):
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0

def create_grid(locked_pos={}):
    grid = [[BLACK for _ in range(10)] for _ in range(20)]
    for y in range(len(grid)):
        for x in range(len(grid[y])):
            if (x, y) in locked_pos:
                grid[y][x] = locked_pos[(x, y)]
    return grid

def convert_shape_format(piece):
    positions = []
    form = piece.shape[piece.rotation % len(piece.shape)]
    for i, row in enumerate(form):
        for j, column in enumerate(list(row)):
            if column == '0':
                positions.append((piece.x + j, piece.y + i))
    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4) 
    return positions

def valid_space(piece, grid):
    accepted_pos = [[(j, i) for j in range(10) if grid[i][j] == BLACK] for i in range(20)]
    accepted_pos = [j for sub in accepted_pos for j in sub]
    formatted = convert_shape_format(piece)
    for pos in formatted:
        x, y = pos
        if y < 0: continue
        if 0 <= x < 10 and 0 <= y < 20: 
            if pos not in accepted_pos: return False
        elif x < 0 or x >= 10 or y >= 20: return False
    return True

def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1: return True
    return False

def get_random_shape():
    return Piece(5, 0, random.choice(shapes))

def draw_text_middle(surface, text, size, color):
    font = pygame.font.SysFont("comicsans", size, bold=True)
    label = font.render(text, 1, color)
    surface.blit(label, (TOP_LEFT_X + PLAY_WIDTH/2 - (label.get_width()/2), TOP_LEFT_Y + PLAY_HEIGHT/2 - (label.get_height()/2)))

def draw_grid(surface, grid):
    sx = TOP_LEFT_X
    sy = TOP_LEFT_Y
    for i in range(len(grid)): 
        pygame.draw.line(surface, GRAY, (sx, sy + i * BLOCK_SIZE), (sx + PLAY_WIDTH, sy + i * BLOCK_SIZE))
        for j in range(len(grid[i])): 
            pygame.draw.line(surface, GRAY, (sx + j * BLOCK_SIZE, sy), (sx + j * BLOCK_SIZE, sy + PLAY_HEIGHT))

def clear_rows(grid, locked):
    increment = 0 
    for i in range(len(grid)-1, -1, -1):
        row = grid[i]
        if BLACK not in row:
            increment += 1
            ind = i 
            for j in range(len(row)):
                try: del locked[(j, i)]
                except: continue
    if increment > 0:
        for key in sorted(list(locked), key=lambda x: x[1]):
            x, y = key
            if y < ind:
                newKey = (x, y + increment)
                locked[newKey] = locked.pop(key)
    if increment == 1: return 10
    elif increment == 2: return 30
    elif increment == 3: return 50
    elif increment == 4: return 80
    return 0

def draw_window(surface, grid, score=0, time_elapsed=0):
    surface.fill(BLACK)
    font = pygame.font.SysFont('comicsans', 60)
    label = font.render('TETRIS', 1, WHITE)
    surface.blit(label, (TOP_LEFT_X + PLAY_WIDTH / 2 - (label.get_width() / 2), 30))
    font_score = pygame.font.SysFont('comicsans', 30)
    label_score = font_score.render(f'Score: {score}', 1, WHITE)
    surface.blit(label_score, (S_WIDTH - 200, 300))
    label_time = font_score.render(f'Time: {int(time_elapsed)}s', 1, WHITE)
    surface.blit(label_time, (S_WIDTH - 200, 350))
    for y in range(len(grid)):
        for x in range(len(grid[y])):
            pygame.draw.rect(surface, grid[y][x], (TOP_LEFT_X + x * BLOCK_SIZE, TOP_LEFT_Y + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
    pygame.draw.rect(surface, RED, (TOP_LEFT_X, TOP_LEFT_Y, PLAY_WIDTH, PLAY_HEIGHT), 5)
    draw_grid(surface, grid)
    pygame.display.update()

# --- Camera Control Function (Final Stabilized Version with Cross-Hand Rotation) ---
def camera_control(cap, current_piece, grid, last_move_time, move_delay, background_subtractor):
    """Detects body movement for horizontal control and two hands for rotation."""
    
    ret, frame = cap.read()
    if not ret:
        return last_move_time, False 

    # OPTIMIZATION: Reduce Image Size
    scale_factor = 0.5 
    small_frame = cv2.resize(frame, (0, 0), fx=scale_factor, fy=scale_factor)
    
    h, w, _ = small_frame.shape 
    center_x = w // 2 
    
    now = pygame.time.get_ticks()

    if now - last_move_time > move_delay:
        
        # 1. ROTATION CONTROL (Crossed Hands - Two separate contours)
        
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        CONTOUR_AREA_THRESHOLD = 7000 
        
        roi_top_half = small_frame[0:h//2, 0:w]
        roi_left = roi_top_half[0:h//2, 0:w//2]
        roi_right = roi_top_half[0:h//2, w//2:w]
        
        hand_detected_left = False
        hand_detected_right = False
        
        # Process Left ROI
        hsv_left = cv2.cvtColor(roi_left, cv2.COLOR_BGR2HSV)
        mask_left = cv2.inRange(hsv_left, lower_skin, upper_skin)
        contours_left, _ = cv2.findContours(mask_left, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if contours_left:
            max_contour_left = max(contours_left, key=cv2.contourArea)
            if cv2.contourArea(max_contour_left) > CONTOUR_AREA_THRESHOLD:
                hand_detected_left = True
        
        # Process Right ROI
        hsv_right = cv2.cvtColor(roi_right, cv2.COLOR_BGR2HSV)
        mask_right = cv2.inRange(hsv_right, lower_skin, upper_skin)
        contours_right, _ = cv2.findContours(mask_right, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if contours_right:
            max_contour_right = max(contours_right, key=cv2.contourArea)
            if cv2.contourArea(max_contour_right) > CONTOUR_AREA_THRESHOLD:
                hand_detected_right = True

        # Check for Rotation condition (Both hands detected)
        if hand_detected_left and hand_detected_right:
            current_piece.rotation = (current_piece.rotation + 1) % len(current_piece.shape)
            if not valid_space(current_piece, grid):
                current_piece.rotation = (current_piece.rotation - 1) % len(current_piece.shape)
            else:
                last_move_time = now 
                return last_move_time, True
        
        # 2. HORIZONTAL CONTROL (Body Movement - Background Subtraction)
        
        fg_mask = background_subtractor.apply(small_frame)
        fg_mask = cv2.erode(fg_mask, None, iterations=2)
        fg_mask = cv2.dilate(fg_mask, None, iterations=2)
        
        moving_contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if moving_contours:
            largest_moving_contour = max(moving_contours, key=cv2.contourArea)
            
            if cv2.contourArea(largest_moving_contour) > 5000: 
                M = cv2.moments(largest_moving_contour)
                if M["m00"] != 0:
                    body_center_x = int(M["m10"] / M["m00"])
                    
                    THRESHOLD_X = 50 

                 
                    if body_center_x < center_x - THRESHOLD_X:
                        current_piece.x -= 1 
                        if not valid_space(current_piece, grid):
                            current_piece.x += 1 
                        else:
                            last_move_time = now
                            return last_move_time, True

                    
                    elif body_center_x > center_x + THRESHOLD_X:
                        current_piece.x += 1 
                        if not valid_space(current_piece, grid):
                            current_piece.x -= 1
                        else:
                            last_move_time = now
                            return last_move_time, True

    return last_move_time, False 

# --- Main Game Loop ---

def main(win):
    """Main game loop"""
    locked_positions = {}
    run = True
    current_piece = get_random_shape()
    next_piece = get_random_shape()
    clock = pygame.time.Clock()

    # Camera Initialization
    cap = cv2.VideoCapture(0)
    
    # Background Subtractor for Body Movement
    background_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=16, detectShadows=True)
    
    # Camera Control Timers
    last_move_time = pygame.time.get_ticks() 
    MOVE_DELAY = 200 

    fall_time = 0
    fall_speed = 0.27 
    level_time = 0
    start_time = time.time()
    score = 0 

    while run:
        time_elapsed = time.time() - start_time
        grid = create_grid(locked_positions)

        # Speed Up Over Time
        level_time += clock.get_rawtime()
        if level_time/1000 > 60:
            level_time = 0
            if fall_speed > 0.05:
                 fall_speed -= 0.01

        fall_time += clock.get_rawtime()
        clock.tick(60) 

        # Automatic drop
        if fall_time/1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        # --- CAMERA CONTROL INTEGRATION POINT ---
        last_move_time, moved = camera_control(cap, current_piece, grid, last_move_time, MOVE_DELAY, background_subtractor)
        
        # Event Handling (Key Presses) - Kept for backup control
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid): current_piece.x += 1
                
                if event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid): current_piece.x -= 1
                
                if event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid): current_piece.y -= 1

                if event.key == pygame.K_UP:
                    current_piece.rotation = (current_piece.rotation + 1) % len(current_piece.shape)
                    if not valid_space(current_piece, grid): current_piece.rotation = (current_piece.rotation - 1) % len(current_piece.shape)

        # Draw the falling piece to the grid
        shape_pos = convert_shape_format(current_piece)
        
        for pos in shape_pos:
            x, y = pos
            if y > -1:
                grid[y][x] = current_piece.color
        
        # Check if piece landed
        if 'change_piece' in locals() and change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            
            current_piece = next_piece
            next_piece = get_random_shape()
            change_piece = False
            del locals()['change_piece']
            
            # Clear rows and update score
            score_increment = clear_rows(grid, locked_positions)
            score += score_increment

        # Game Over Check
        if check_lost(locked_positions):
            run = False
            draw_text_middle(win, "GAME OVER", 80, RED)
            pygame.display.update()
            pygame.time.delay(2000)

        # Draw the screen
        draw_window(win, grid, score, time_elapsed)

    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()

# --- Pygame Initialization and Main Loop Execution ---

if __name__ == '__main__':
    pygame.init()
    win = pygame.display.set_mode((S_WIDTH, S_HEIGHT))
    pygame.display.set_caption('Python Tetris')
    main(win)