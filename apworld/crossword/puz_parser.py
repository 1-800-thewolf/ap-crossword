from .Types import ClueId, ClueInfo, CrossLetter, Direction, ParsedPuz


def parse_grid_layout(data: bytes) -> dict:
    """
    Grid shape of a .puz file, without the solution letters.

    Returns a dict with width, height, layout (one string per row, '#' = black square,
    '-' = letter square), circles (indices of circled squares) and title/author.
    """
    width = data[0x2C]
    height = data[0x2D]
    grid_size = width * height
    solution = data[0x34:0x34 + grid_size].decode('latin-1')
    layout = ["".join('#' if ch == '.' else '-' for ch in solution[row * width:(row + 1) * width])
              for row in range(height)]

    strings_offset = 0x34 + 2 * grid_size
    title, author = (s.decode('latin-1') for s in data[strings_offset:].split(b'\0', 2)[:2])

    # GEXT extension holds per-square markup; 0x80 marks a circled square
    circles = []
    gext = data.find(b'GEXT', strings_offset)
    if gext != -1:
        markup = data[gext + 8:gext + 8 + grid_size]
        circles = [i for i, flags in enumerate(markup) if flags & 0x80]

    return {"width": width, "height": height, "layout": layout, "circles": circles,
            "title": title, "author": author}


def parse_puz(data: bytes) -> tuple[dict[ClueId, ClueInfo], list[tuple[str, list[tuple[ClueId, int]]]]]:
    """
    Parse a .puz file.

    Args:
        data: The binary contents of a .puz file

    Returns:
        A tuple containing:
        - dict mapping ClueId to ClueInfo (with clue text and answer)
        - list of letters in the grid, each with their ClueId(s) and position in answer
    """
    # Parse header
    width = data[0x2C]
    height = data[0x2D]

    # Parse solution grid (starts at offset 0x34 = 52)
    grid_size = width * height
    solution_offset = 0x34
    solution = data[solution_offset:solution_offset + grid_size].decode('ascii')

    # Skip player state grid (same size as solution)
    strings_offset = solution_offset + 2 * grid_size

    # Parse null-terminated strings
    def read_string(offset):
        end = offset
        while data[end] != 0:
            end += 1
        # Technically is the valid one but I've seen both in the wild and would like to try to have support
        try:
            return data[offset:end].decode('utf-8'), end + 1
        except:
            return data[offset:end].decode('latin-1'), end + 1

    # Read title, author, copyright
    title, strings_offset = read_string(strings_offset)
    author, strings_offset = read_string(strings_offset)
    copyright_text, strings_offset = read_string(strings_offset)

    # Read all clues
    clue_strings = []
    while strings_offset < len(data):
        # Check if we've hit extension sections (they start with specific markers)
        if strings_offset + 8 <= len(data):
            # Extensions have format: title (4 bytes), length (2 bytes), checksum (2 bytes)
            potential_ext = data[strings_offset:strings_offset + 4]
            if potential_ext in [b'GEXT', b'LTIM', b'GRBS', b'RTBL', b'RUSR']:
                break

        try:
            clue, strings_offset = read_string(strings_offset)
            if clue:  # Only add non-empty clues
                clue_strings.append(clue)
        except:
            break

    # Build grid numbering and clue mapping
    # Create grid as 2D array for easier navigation
    grid = []
    for row in range(height):
        grid.append(list(solution[row * width:(row + 1) * width]))

    # Number the grid cells
    cell_numbers = [[0] * width for _ in range(height)]
    clue_number = 1

    for row in range(height):
        for col in range(width):
            if grid[row][col] != '.':
                # A cell gets a number if:
                # 1. It's the start of an across word (cell to left is black/edge and cell to right exists and is not black)
                # 2. It's the start of a down word (cell above is black/edge and cell below exists and is not black)

                is_across_start = False
                is_down_start = False

                # Check across - needs to be start of word (nothing to left or black to left)
                # AND have at least one more letter to the right
                if (col == 0 or grid[row][col - 1] == '.') and (col < width - 1 and grid[row][col + 1] != '.'):
                    is_across_start = True

                # Check down - needs to be start of word (nothing above or black above)
                # AND have at least one more letter below
                if (row == 0 or grid[row - 1][col] == '.') and (row < height - 1 and grid[row + 1][col] != '.'):
                    is_down_start = True

                if is_across_start or is_down_start:
                    cell_numbers[row][col] = clue_number
                    clue_number += 1

    # Build clue map and extract answers
    # Clues are stored in the file by clue number order, with across before down for each number
    clue_map = {}

    # First, collect all numbered cells with their answers
    number_info = {}  # number -> {'across': answer or None, 'down': answer or None}

    for row in range(height):
        for col in range(width):
            num = cell_numbers[row][col]
            if num > 0:
                if num not in number_info:
                    number_info[num] = {'across': None, 'down': None}

                # Check if this starts an across clue
                if (col == 0 or grid[row][col - 1] == '.') and col < width - 1 and grid[row][col + 1] != '.':
                    answer = ""
                    c = col
                    while c < width and grid[row][c] != '.':
                        answer += grid[row][c]
                        c += 1
                    number_info[num]['across'] = answer

                # Check if this starts a down clue
                if (row == 0 or grid[row - 1][col] == '.') and row < height - 1 and grid[row + 1][col] != '.':
                    answer = ""
                    r = row
                    while r < height and grid[r][col] != '.':
                        answer += grid[r][col]
                        r += 1
                    number_info[num]['down'] = answer

    # Now match clues to answers in order
    clue_idx = 0
    for num in sorted(number_info.keys()):
        # Across clue comes first for this number (if it exists)
        if number_info[num]['across'] is not None:
            if clue_idx < len(clue_strings):
                clue_id = ClueId(Direction.ACROSS, num)
                clue_map[clue_id] = ClueInfo(clue_strings[clue_idx], number_info[num]['across'])
                clue_idx += 1

        # Down clue comes second for this number (if it exists)
        if number_info[num]['down'] is not None:
            if clue_idx < len(clue_strings):
                clue_id = ClueId(Direction.DOWN, num)
                clue_map[clue_id] = ClueInfo(clue_strings[clue_idx], number_info[num]['down'])
                clue_idx += 1

    # Build letter list with clue associations
    letter_list = []

    for row in range(height):
        for col in range(width):
            if grid[row][col] != '.':
                letter = grid[row][col]
                associations = []

                # Find across clue for this cell
                # Trace back to find the start of the across word
                start_col = col
                while start_col > 0 and grid[row][start_col - 1] != '.':
                    start_col -= 1

                # Check if this is part of an across word
                if (start_col < width - 1 and grid[row][start_col + 1] != '.') or \
                   (start_col == col and col < width - 1 and grid[row][col + 1] != '.') or \
                   (start_col < col):
                    # Find the clue number for this across word
                    across_num = cell_numbers[row][start_col]
                    if across_num > 0:
                        position_in_word = col - start_col
                        clue_id = ClueId(Direction.ACROSS, across_num)
                        associations.append((clue_id, position_in_word))

                # Find down clue for this cell
                # Trace up to find the start of the down word
                start_row = row
                while start_row > 0 and grid[start_row - 1][col] != '.':
                    start_row -= 1

                # Check if this is part of a down word
                if (start_row < height - 1 and grid[start_row + 1][col] != '.') or \
                   (start_row == row and row < height - 1 and grid[row + 1][col] != '.') or \
                   (start_row < row):
                    # Find the clue number for this down word
                    down_num = cell_numbers[start_row][col]
                    if down_num > 0:
                        position_in_word = row - start_row
                        clue_id = ClueId(Direction.DOWN, down_num)
                        associations.append((clue_id, position_in_word))

                letter_list.append((letter, associations))

    return clue_map, letter_list
