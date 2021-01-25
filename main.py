import pygame as pg
import block
import sys
import random

pg.init()

screen_w = 800
screen_h = 700
basic_block_size = 30
space_to_play_w = 300
space_to_play_h = 600
top_left_x = (screen_w - space_to_play_w) // 2
top_left_y = screen_h - space_to_play_h


def create_grid(occupied_positions):
    grid = [[(0, 0, 0) for x in range(10)] for y in range(20)]
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if(j, i) in occupied_positions:
                grid[i][j] = occupied_positions[(j, i)]
    return grid


def draw_grid(grid):
    x = top_left_x
    y = top_left_y

    for i in range(1, len(grid), 1):
        pg.draw.line(window, (128, 128, 128), (x, y + i*basic_block_size), (x + space_to_play_w, y + i*basic_block_size))
        for j in range(1, len(grid[i]), 1):
            pg.draw.line(window, (128, 128, 128), (x + j*basic_block_size, y), (x + j*basic_block_size, y + space_to_play_h))


def draw_mid_text(text, size, color):
    font = pg.font.SysFont("Arial", size, bold=True)
    label = font.render(text, True, color)
    window.blit(label, (top_left_x + space_to_play_w/2 - (label.get_width()/2), top_left_y + space_to_play_h/2 - label.get_height()/2))


def convert_block_format(block):
    positions = []
    format = block.block_type[block.rotation % len(block.block_type)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '1':
                positions.append((block.x + j, block.y + i))

    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)

    return positions


def valid_space(block, grid):
    accepted_position = [[(j, i) for j in range(10) if grid[i][j] == (0, 0, 0)] for i in range(20)]
    accepted_position = [j for sub in accepted_position for j in sub]

    formatted = convert_block_format(block)

    for pos in formatted:
        if pos not in accepted_position:
            if pos[1] > -1:
                return False
    return True


def clear_rows(grid, occupied_positions):

    counter = 0
    for i in range(len(grid) - 1, -1, -1):
        row = grid[i]
        if (0, 0, 0) not in row:
            counter += 1
            index = i
            for j in range(len(row)):
                try:
                    del occupied_positions[(j, i)]
                except:
                    continue

    if counter > 0:
        for key in sorted(list(occupied_positions), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < index:
                newKey = (x, y + counter)
                occupied_positions[newKey] = occupied_positions.pop(key)
    return counter


def draw_next_block(block):
    font = pg.font.SysFont("Arial", 28)
    label = font.render('Next Block: ', True, (255, 255, 255))

    x = top_left_x + space_to_play_w + 60
    y = top_left_y + space_to_play_h/2 - 100
    format = block.block_type[block.rotation % len(block.block_type)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column, in enumerate(row):
            if column == '1':
                pg.draw.rect(window, block.color, (x + j*basic_block_size, y + i*basic_block_size, basic_block_size, basic_block_size), border_radius=10)

    window.blit(label, (x + 10, y - 35))


def draw_window(grid, score=0):
    window.fill((18, 57, 107))
    font = pg.font.SysFont("Arial", 54)
    label = font.render("TETRIS", True, (0, 255, 0))
    window.blit(label, (top_left_x + space_to_play_w / 2 - (label.get_width() / 2), 30))

    font = pg.font.SysFont("Arial", 28)
    label = font.render('Score: ' + str(score), True, (255, 255, 255))

    x = top_left_x + space_to_play_w + 50
    y = top_left_y + space_to_play_h / 2 - 100

    window.blit(label, (x + 20, y + 170))

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pg.draw.rect(window, grid[i][j], (top_left_x + j * basic_block_size, top_left_y + i * basic_block_size, basic_block_size, basic_block_size), border_radius=10)

    pg.draw.rect(window, (100, 192, 255), (top_left_x, top_left_y, space_to_play_w, space_to_play_h), 5, border_radius=10)

    draw_grid(grid)


def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False


def main():
    occupied_positions = {}
    game_on = True
    change_block = False
    next_block = block.Block.get_block()
    current_block = block.Block.get_block()
    pg_clock = pg.time.Clock()
    fall_time = 0
    pause = False
    score = 0
    last_score = score
    fall_speed = 0.3

    while game_on:

        grid = create_grid(occupied_positions)
        fall_time += pg_clock.get_rawtime()
        pg_clock.tick()

        if fall_time/1000 >= fall_speed:
            fall_time = 0
            current_block.y += 1
            if not(valid_space(current_block, grid)) and current_block.y > 0:
                current_block.y -= 1
                change_block = True

        if score > last_score:
            last_score = score
            fall_speed -= 0.01

        for event in pg.event.get():
            if event.type == pg.QUIT:
                game_on = False
                pg.quit()
                sys.exit()

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_LEFT:
                    current_block.x -= 1
                    if not (valid_space(current_block, grid)):
                        current_block.x += 1
                if event.key == pg.K_RIGHT:
                    current_block.x += 1
                    if not (valid_space(current_block, grid)):
                        current_block.x -= 1
                if event.key == pg.K_DOWN:
                    current_block.y += 1
                    if not (valid_space(current_block, grid)):
                        current_block.y -= 1

                if event.key == pg.K_UP:
                    current_block.rotation += 1
                    if not(valid_space(current_block, grid)):
                        current_block.rotation -= 1
                if event.key == pg.K_p:
                    pause = True
                if event.key == pg.K_r:
                    # reset
                    game_on = False

        while(pause):
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_p:
                        pause = False

        block_pos = convert_block_format(current_block)

        for i in range(len(block_pos)):
            x, y = block_pos[i]
            if y > -1:
                grid[y][x] = current_block.color

        if change_block:
            for pos in block_pos:
                p = (pos[0], pos[1])
                occupied_positions[p] = current_block.color
            current_block = next_block
            next_block = block.Block.get_block()
            change_block = False
            score += clear_rows(grid, occupied_positions) * 10

        draw_window(grid, score)
        draw_next_block(next_block)
        pg.display.update()

        if check_lost(occupied_positions):
            draw_mid_text("You Lost! Your score: " + str(score), 40, (255, 0, 0))
            pg.display.update()
            pg.time.delay(1400)
            game_on = False


def main_menu():
    game_on = True
    while game_on:
        window.fill((18, 57, 107))
        draw_mid_text("Press Any Key To Play", 58, (255, 255, 255))
        pg.display.update()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                game_on = False

            if event.type == pg.KEYDOWN:
                main()

    pg.quit()
    sys.exit()


window = pg.display.set_mode((screen_w, screen_h))
pg.display.set_caption('Tetris')


if __name__ == '__main__':
    main_menu()
