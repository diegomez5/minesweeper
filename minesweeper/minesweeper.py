import random
import pygame
from datetime import datetime


TILE_SIZE = 30
BANNER_SIZE = 2.5 * TILE_SIZE
game_completed = False

COLORS = {
    1: '#0000ff',
    2: '#00FF00',
    3: '#FF0000',
    4: '#00008b',
    5: '#8b0000',
    6: '#14A3C7',
    7: '#000000',
    8: '#808080'
}

DIFFICULTIES = {
    'Easy': [10, 8, 10],
    'Medium': [18, 14, 40],
    'Hard': [24, 20, 99]
}

def main(settings):
    global game_completed
    game_completed = False

    pygame.init()
    pygame.display.set_caption('Minesweeper')

    before_time = round(datetime.today().timestamp())

    x_len, y_len, num_mines = [settings[i] for i in range(len(settings))]
    board = ''
    perimeter = calculate_perimeter(x_len, y_len)
    screen = pygame.display.set_mode((perimeter[0], perimeter[1]))

    font_size = round(BANNER_SIZE / 3) if x_len == 10 else round(BANNER_SIZE / 2)
    font = pygame.font.SysFont("monospace", font_size)
   
    tiles = []
    subset_tiles = []
    square_color = False
    data = calculate_coordinates(x_len, y_len)
    for i, set in enumerate(data):
        if i % x_len == 0 and i != 0:
            tiles.append(subset_tiles)
            subset_tiles = []
            if x_len % 2 == 0: 
                square_color = not square_color
        square_color = not square_color
        subset_tiles.append(Tile(set[0], set[1], TILE_SIZE, TILE_SIZE, square_color, screen, x_len, y_len, num_mines))
    tiles.append(subset_tiles)

    difficulty_buttons = []
    for i, difficulty in enumerate(DIFFICULTIES.keys()):
        size = (BANNER_SIZE / 2)
        
        x_pos = (x_len / 15) * (size * i)
        y_pos = BANNER_SIZE / 4
        difficulty_buttons.append(Difficulty_Button(screen, x_pos, y_pos, size, difficulty))


    while True:
        event = pygame.event.poll() 
        if event.type == pygame.QUIT:
            pygame.quit()
            return False

        screen.fill('#4EA3B7')

        mouse_state = pygame.mouse.get_pressed(num_buttons=3)
        for y, row in enumerate(tiles):
            for x, tile in enumerate(row):
                if not tile.board: 
                    tile.board = board
                tile.render()

                if board == '' and tile.board: 
                    board = tile.board

                tile.render_event()
                if tile.chorded:
                    chordable = chord(tiles, board, [x, y])
                    if chordable['can_chord']:
                        for coordinate in chordable['tiles']:
                            if board[coordinate[1]][coordinate[0]] == 0:
                                tile.nearby = nearby_empty(board, coordinate)
                            else:
                                tiles[coordinate[1]][coordinate[0]].mined = True
                                tiles[coordinate[1]][coordinate[0]].color = ['#808080', '#BEBEBE'] if tiles[coordinate[1]][coordinate[0]].dark else ['#949494', '#BEBEBE']
                        tile.chorded = False
                    else: 
                        if mouse_state[1]:
                            for coordinate in chordable['tiles']:
                               tiles[coordinate[1]][coordinate[0]].chorded = False
                            chordable = chord(tiles, board, mouse_pos(tiles)) 
                            for coordinate in chordable['tiles']:
                                tiles[coordinate[1]][coordinate[0]].chorded = 'highlight'
                        else:
                            tile.chorded = False

                if tile.nearby:
                    for near in tile.nearby['empty']:
                        tiles[near[1]][near[0]].color = ['#808080', '#BEBEBE'] if tiles[near[1]][near[0]].dark else ['#949494', '#BEBEBE']
                    for num in tile.nearby['nums']:
                        tiles[num[1]][num[0]].mined = True
                        tiles[num[1]][num[0]].color = ['#808080', '#BEBEBE'] if tiles[num[1]][num[0]].dark else ['#949494', '#BEBEBE']
                    tile.nearby = False

        # render difficulty buttons
        for button in difficulty_buttons:
            button.render()
            if button.clicked:
                return DIFFICULTIES[button.difficulty]


        if not game_completed:
            if not (game_finished(tiles, num_mines)):
                flags = num_flagged(tiles, num_mines)
                flag_label = font.render(f"flags: {flags} time: {round(datetime.today().timestamp()) - before_time}", 0.1, '#000000')
        screen.blit(flag_label, ((x_len / 10) * ((BANNER_SIZE) + (x_len / 2)), BANNER_SIZE / 4))
        

        pygame.display.flip()

class Difficulty_Button():
    def __init__(self, screen, x, y, size, difficulty):
        self.screen = screen

        self.x = x
        self.y = y
        self.size = size
        self.difficulty = difficulty

        self.clicked = False

        self.surface = pygame.Surface((size, size))
        self.hitbox = pygame.Rect(x, y, size, size)
        self.color = '#808080'

        font = pygame.font.SysFont("monospace", round(size))
        self.label = font.render(f"{difficulty[0]}", 0.1, '#000000')

    def render(self):
        if self.hitbox.collidepoint(pygame.mouse.get_pos()):
            self.color = '#BEBEBE'
            mouse_state = pygame.mouse.get_pressed(num_buttons=3)
            if mouse_state[0]:
                self.clicked = True
        else: 
            self.color = '#808080'
        self.surface.fill(self.color)
        self.screen.blit(self.surface, self.hitbox)
        self.screen.blit(self.label, (self.x + self.size / 5, self.y))


def mouse_pos(tiles):
    for y in tiles:
        for tile in y:
            if tile.hitbox.collidepoint(pygame.mouse.get_pos()):
                coordinate = [int(tile.x / TILE_SIZE), int((tile.y - BANNER_SIZE) / TILE_SIZE)]
                return coordinate

def num_flagged(squares, num_mines):
    for row in squares:
        for square in row:
            if square.flagged:
                num_mines -= 1
    return num_mines

def calculate_coordinates(width, height):
    return [[x * TILE_SIZE, (y * TILE_SIZE) + BANNER_SIZE] for y in range(height) for x in range(width)]

def calculate_perimeter(width, height):
    return [width * TILE_SIZE, BANNER_SIZE + (height * TILE_SIZE)]

def game_finished(tiles, num_mines):
    left = 0
    for row in tiles:
        for tile in row:
            if tile.color[1] == '#bbe8eb':
                left += 1
    return num_mines == left

def chord(tiles, board, tile):
    global game_completed
    can_chord = False
    tile_num = board[tile[1]][tile[0]]
    if tile_num == 'm' or tile_num == 0: return {'tiles': [], 'can_chord': False}
    if tiles[tile[1]][tile[0]].color[1] == '#bbe8eb': return {'tiles': [], 'can_chord': False}

    valid = valid_surrounding(board, tile)
    for coordinate in valid:
        if tiles[coordinate[1]][coordinate[0]].flagged:
            if board[coordinate[1]][coordinate[0]] != 'm':
                game_completed = True
                return {'tiles': [], 'can_chord': False}
            tile_num -= 1

    if tile_num == 0:
        can_chord = True
    
    chordable = []
    for coordinate in valid:
        if tiles[coordinate[1]][coordinate[0]].color[1] == '#BEBEBE': continue
        if tiles[coordinate[1]][coordinate[0]].flagged and not can_chord: continue
        if board[coordinate[1]][coordinate[0]] == 'm' and can_chord: continue
        chordable.append(coordinate)
    return {'tiles': chordable, 'can_chord': can_chord}



def valid_surrounding(board, tile):
    surrounding = []
    for i in [tile[0] - 1, tile[0], tile[0] + 1]:
        if -1 < i < len(board[0]):
            if tile[1] - 1 >= 0:
                surrounding.append([i, tile[1] - 1])
            if tile[1] + 1 < len(board):
                surrounding.append([i, tile[1] + 1])
    for i in [tile[0] - 1, tile[0] + 1]:
        if -1 < i < len(board[0]):
            surrounding.append([i, tile[1]])
    return surrounding



class Tile():
    def __init__(self, x, y, width, height, dark, screen, x_len, y_len, num_mines):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.dark = dark
        self.color = ['#63c7de', '#bbe8eb'] if dark else ['#79d0e1', '#bbe8eb']
        self.screen = screen

        self.board = ''
        self.x_len = x_len
        self.y_len = y_len
        self.num_mines = num_mines

        self.flag_image = pygame.image.load('flag.png')
        self.flag_image = pygame.transform.scale(self.flag_image, (TILE_SIZE, TILE_SIZE))
        self.bomb_image = pygame.image.load('bomb.png')
        self.bomb_image = pygame.transform.scale(self.bomb_image, (TILE_SIZE, TILE_SIZE))
        self.flagged = False

        self.chorded = False
        self.mined = False
        self.nearby = False

        self.clicked = False

        self.surface = pygame.Surface((self.width, self.height))
        self.hitbox = pygame.Rect(self.x, self.y, self.width, self.height)

    def render(self):
        global game_completed

        self.surface.fill(self.color[0])
        
        if game_completed:
            self.flagged = False
            if self.board[int((self.y - BANNER_SIZE) / TILE_SIZE)][int(self.x / TILE_SIZE)] == 'm':
                self.color = ['#808080', '#BEBEBE'] if self.dark else ['#949494', '#BEBEBE']
                self.screen.blit(self.surface, self.hitbox)
                self.screen.blit(self.bomb_image, (self.x, self.y))
                return
            
        if self.chorded == 'highlight':
            self.surface.fill(self.color[1])
        if self.hitbox.collidepoint(pygame.mouse.get_pos()):
            self.surface.fill(self.color[1])

            mouse_state = pygame.mouse.get_pressed(num_buttons=3)
            if mouse_state[0] ^ mouse_state[1] ^ mouse_state[2]:
                if not self.clicked and not game_completed:
                    self.clicked = True
                    event = 'mine' if mouse_state[0] else 'flag' if mouse_state[2] else 'chord'
                    self.handler(event)
            else: 
                self.clicked = False
        self.screen.blit(self.surface, self.hitbox)

    def handler(self, event):
        global game_completed
        if event == 'mine':
            if self.board == '':
                mined_tile = [int(self.x / TILE_SIZE), int((self.y - BANNER_SIZE) / TILE_SIZE)]
                self.board = make_board(self.x_len, self.y_len, self.num_mines, mined_tile)
                self.board = make_completed_board(self.board)

            space = self.board[int((self.y - BANNER_SIZE) / TILE_SIZE)][int(self.x / TILE_SIZE)]
            if space == 'm':
                game_completed = True
                self.screen.blit(self.surface, self.hitbox)
            else:
                self.color = ['#808080', '#BEBEBE'] if self.dark else ['#949494', '#BEBEBE']
                if space != 0:
                    self.mined = True
                else:
                    coordinate = [int(self.x / TILE_SIZE), int((self.y - BANNER_SIZE) / TILE_SIZE)]
                    self.nearby = nearby_empty(self.board, coordinate)
        if event == 'flag':
            self.flagged = not self.flagged
        if event == 'chord':
            self.chorded = True

    def render_event(self):
        if self.flagged:
            if self.color[1] == '#BEBEBE':
                self.flagged = False
            else:
                self.screen.blit(self.flag_image, (self.x, self.y))
        if self.mined:
            space = self.board[int((self.y - BANNER_SIZE) / TILE_SIZE)][int(self.x / TILE_SIZE)]
            font = pygame.font.SysFont("monospace", TILE_SIZE, True)
            label = font.render(f"{space}", 0.1, COLORS[space])
            self.screen.blit(label, (self.x + TILE_SIZE / 5, self.y))


#14 18 standard size
def make_board(x, y, mines, exclude):
    board = random.sample(['m' if i < mines else 0 for i in range(x * y)], x * y)
    board = [board[slice((j * x), (j * x) + x)] for j in range(y)]

    clicked_square = exclude
    exclude = valid_surrounding(board, exclude)
    exclude.append(clicked_square)
    for pair in exclude:
        if board[pair[1]][pair[0]] == 'm':
            board[pair[1]][pair[0]] = 0
            new_spot = [random.randint(0, x - 1), random.randint(0, y - 1)]
            while board[new_spot[1]][new_spot[0]] == 'm' or new_spot == pair:
                new_spot = [random.randint(0, x - 1), random.randint(0, y - 1)]
            board[new_spot[1]][new_spot[0]] = 'm'
    return board

# probably could make this more efficent idk
def make_completed_board(board):
    for y, row in enumerate(board):
        for x, space in enumerate(row):
            if (space != 'm'): continue
            # top
            if (y - 1 >= 0): 
                for i in [x - 1, x, x + 1]:
                    if -1 < i < len(row) and board[y - 1][i] != 'm':
                        board[y - 1][i] += 1
            # sides
            for i in [x - 1, x + 1]:
                if -1 < i < len(row) and board[y][i] != 'm':
                    board[y][i] += 1
            # bottom
            if (y + 1 < len(board)): 
                for i in [x - 1, x, x + 1]:
                    if -1 < i < len(row) and board[y + 1][i] != 'm':
                        board[y + 1][i] += 1
    return board

# i know this is inefficient
def nearby_empty(board, tile):
    empty_tiles = [tile]
    run = True
    while run:
        length = len(empty_tiles)
        for empty in empty_tiles:
            if (empty[1] - 1 >= 0): 
                for i in [empty[0] - 1, empty[0], empty[0] + 1]:
                    if -1 < i < len(board[0]) and board[empty[1] - 1][i] == 0:
                        if [i, empty[1] - 1] not in empty_tiles:
                            empty_tiles.append([i, empty[1] - 1])

            for i in [empty[0] - 1, empty[0] + 1]:
                if -1 < i < len(board[0]) and board[empty[1]][i] == 0:
                    if [i, empty[1]] not in empty_tiles:
                        empty_tiles.append([i, empty[1]])

            if (empty[1] + 1 < len(board)): 
                for i in [empty[0] - 1, empty[0], empty[0] + 1]:
                    if -1 < i < len(board[0]) and board[empty[1] + 1][i] == 0:
                        if [i, empty[1] + 1] not in empty_tiles:
                            empty_tiles.append([i, empty[1] + 1])
        if length == len(empty_tiles): 
            run = False
    # make this more efficient
    nearby_nums = []
    for y, row in enumerate(board):
        for x, space in enumerate(row):
            if (space == 0): continue
            # top
            if (y - 1 >= 0): 
                for i in [x - 1, x, x + 1]:
                    if -1 < i < len(row) and [i, y - 1] in empty_tiles:
                        if [x, y] not in nearby_nums:
                            nearby_nums.append([x, y])
            # sides
            for i in [x - 1, x + 1]:
                if -1 < i < len(row) and [i, y] in empty_tiles:
                    if [x, y] not in nearby_nums:
                        nearby_nums.append([x, y])
            # bottom
            if (y + 1 < len(board)): 
                for i in [x - 1, x, x + 1]:
                    if -1 < i < len(row) and [i, y + 1] in empty_tiles:
                        if [x, y] not in nearby_nums:
                            nearby_nums.append([x, y])
            pass
    return {
        'empty': empty_tiles,
        'nums': nearby_nums
    }


if __name__ == '__main__':
    settings = [18, 14, 40]
    while True:
        settings = main(settings)
        if not settings: 
            break

#TODO: fix cohorfin highlight , change text size on banner
