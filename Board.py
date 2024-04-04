from math import inf


# Square value constants

MAX = "O" # O goes first
MIN = "X"
OPEN = "-"
BLOCKED = "/"


# Evaluation function for non-terminal leaf nodes

# Prefer moves that leave the fewest open squares for the opponent at this
# state, unless that would leave only a single square and thus result in a
# definite loss. Other situations may lead to a definite loss, but they require
# more than the open count to identify.
# Conversely, when the leaf utility comes from a node where the other player
# chooses, this results in preferring moves that result in the most options for
# yourself for any given leaf node.
def _evaluate_node(board):
    util = board._open_cnt
    if util == 1: # Avoid leaving exactly 1 open square
        util = board.width * board.height + 1 # Greater than open count for all states
    
    # Since the parent of this state defines which player is evaluating this
    # choice, board._MAX_turn is True when MIN is determining whether to move
    # to this leaf, so smaller util values are preferred by MIN, and vice versa.
    return util if board._MAX_turn else -util


# To use this class, call create(width, height) to build an initial state, and
# if the function returns an ObstructionBoard instead of None, use the
# following interface:
#   String representation:
#       str constructor
#   New board with another move played:
#       place(row, col)
#   Read-only properties:
#       width, height, MAX_turn, action, done, winner
#   Read/write property:
#       utility
#   Unmanaged read/write variable:
#       chosen_child (expected to be a game tree node, not a bare state)
class ObstructionBoard:
    # Create a new width x height game board, with no moves played and all
    # squares initially open.
    # This function allows the constructor to be reserved for internally
    # creating objects as successor states.
    @classmethod
    def create(cls, width, height):
        return None if width < 1 or height < 1 else\
               cls(
                   [[OPEN] * width for _ in range(height)], # All open squares
                   width * height, True, None
               )

    def __init__(self, tiles, open_cnt, MAX_turn, action):
        # State-related data
        self._tiles = tiles # 2D list of the board's squares
        self._open_cnt = open_cnt # Number of remaining open squares
        self._MAX_turn = MAX_turn

        # AI choice data
        self._action = action # Move made to reach this state
        self._utility = None
        self.chosen_child = None # If not terminal or pruned, which child the AI should choose

    # Construct a string showing the board as a 2D grid with numbered rows and
    # columns.
    def __str__(self):
        return "  " + " ".join([str(i) for i in range(self.width)]) + "\n" \
               + "\n".join([
                   f"{i} " + " ".join(row) for i, row in enumerate(self._tiles)
               ])
    
    # Note that list equality checks element equality.
    # Only the square values need to be compared because this comparison is
    # used only for boards within the same game (which must give the next
    # turn to the same player if the same number of moves have been played
    # because the same player started).
    def __eq__(self, other):
        return self._tiles == other._tiles


    # Successor states

    # If a valid and open square is specified, place the current player's
    # marker in the specified square, block any open squares adjacent to it,
    # and update the count of open squares accordingly.
    def place(self, row, col):
        # The valid rows are [0, height - 1], and the valid columns are
        # [0, width - 1].
        # Only open squares can be played.
        if not (0 <= row < self.height) or not (0 <= col < self.width) \
           or self._tiles[row][col] != OPEN:
            return None
        
        # Copy the old board as a new 2D list (shallow copy each row; note that
        # str is immutable).
        new_squares = [list(old_row) for old_row in self._tiles]
        new_open_cnt = self._open_cnt

        # Place the current player's marker in the specified square.
        new_squares[row][col] = MAX if self._MAX_turn else MIN
        new_open_cnt -= 1

        # Block all open surrounding tiles
        for i in range(row - 1, row + 2):
            if 0 <= i < self.height: # Skip out of range rows
                for j in range(col - 1, col + 2):
                    if 0 <= j < self.width and new_squares[i][j] == OPEN:
                        new_squares[i][j] = BLOCKED
                        new_open_cnt -= 1
        
        # Create a new board with the new state, and switch whose turn it is.
        return ObstructionBoard(
            new_squares, new_open_cnt, not self._MAX_turn, (row, col)
        )


    # Properties

    @property
    def width(self):
        return len(self._tiles[0]) # Column count
    
    @property
    def height(self):
        return len(self._tiles) # Row count

    @property
    def MAX_turn(self):
        return self._MAX_turn

    # The row and column placement to reach this state from its parent
    @property
    def action(self): 
        return self._action

    # Whether this is a terminal state and the game is over
    @property
    def done(self):
        return self._open_cnt == 0

    # There is no winner if there are still open squares, and the winner is
    # otherwise the opposite of the player who has the current turn.
    # This returns None for non-terminal nodes and one of MAX and MIN for
    # terminal nodes.
    @property
    def winner(self):
        return None if not self.done else \
               MIN if self._MAX_turn else MAX
    
    @property
    def utility(self):
        # If the utility is accessed but has not been externally provided, the
        # utility is calculated as a terminal node or non-terminal leaf node.
        if self._utility is None:
            # The utility value of a leaf node is infinity if MAX won,
            # -infinity if MIN won, and the value of the evaluation function if
            # no one has won.
            winner = self.winner
            self._utility = _evaluate_node(self) if winner is None else \
                            inf if winner == MAX else -inf
        
        return self._utility
    
    @utility.setter # For backed up utility for non-leaf nodes
    def utility(self, value):
        self._utility = value
    