# Notes:
#       node[0] is used to access an ObstructionBoard from a tree node. node[i]
#           with i >= 1 is used to access a tree node that is a child. Local
#           variables holding tree nodes will have "tree" or "node" in their
#           names, while local variables holding ObstructionBoard objects
#           directly will have "state" in their names.
#       This program was tested only in Python 3.12.0, and older versions may
#           work but are thus not guaranteed to provide expected behavior.

from inspect import cleandoc
import sys

from Board import ObstructionBoard
from Solver import minimax, minimax_ab


# Utility constants
_LOOKAHEAD_DEPTH = 4

_README = "Readme.txt"
_ALGORITHMS = {
    "MM": lambda state: minimax(state, _LOOKAHEAD_DEPTH),
    "AB": lambda state: minimax_ab(state, _LOOKAHEAD_DEPTH)
}
_SIZES = [(6, 6), (6, 7), (7, 8), (8, 8)]
_SIZE_STRINGS = [f'{size[0]}*{size[1]}' for size in _SIZES]


# Argument validation and processing

# Exception messages from the function are user-readable and safe to show
# externally.
# RuntimeError and ValueError must be handled by the caller
def _parse_args():
    if len(sys.argv) != 4:
        raise RuntimeError(
            "Exactly three arguments are required: "
            "player searchmethod size"
        )
    
    # 1. Player
    if sys.argv[1] not in ("1", "2"):
        raise ValueError(
            "The AI player must be specified as \"1\" (AI goes first) or \"2\""
            " (AI goes second; human goes first)."
        )
    ai_first = sys.argv[1] == "1"

    # 2. Search method
    algorithm_name = sys.argv[2]
    try:
        algorithm = _ALGORITHMS[algorithm_name]
    except KeyError:
        raise ValueError(
            f'"{algorithm_name}" is not a supported algorithm. Choose one of '
            f'the following: {" ".join(_ALGORITHMS.keys())}'
        )

    # 3. Size
    try:
        size_ind = _SIZE_STRINGS.index(sys.argv[3])
    except ValueError:
        raise ValueError(
            f'The size must be one of the following: {" ".join(_SIZE_STRINGS)}'
        )
    size = _SIZES[size_ind]

    return ai_first, algorithm, algorithm_name, size, sys.argv[3]


# Readme output

# Print a description of the initial search
def _print_readme(size, algorithm_name, expanded_cnt):
    try:
        with open(_README, "a") as readme:
            readme.write(cleandoc(f"""
                Size: {size}
                Algorithm: {algorithm_name}
                Expanded: {expanded_cnt}
                Depth: {_LOOKAHEAD_DEPTH}
            """))
            readme.write("\n\n")
    except OSError:
        print(
            f'The results could not be written to "{_README}". Make sure the '
            'program is run with sufficient permissions.'
        )


# Starting and playing the game

def _play_ai_turn(tree, search): # Returns node
    temp_tree = tree[0].chosen_child
    
    # Generate more of the tree if the AI has no defined choice from here. This
    # can occur if the search ended due to depth limits or if some of the
    # children may have been pruned (meaning the AI may not have checked the
    # utility of all legal successors).
    # tree[0].done is guaranteed to be false by the loop condition, so the AI
    # must have some move at this state, so search(tree[0])[0].chosen_child is
    # not None (see the pruning section of _base_minimax() in Solver.py for how
    # this is guaranteed).
    if temp_tree is None:
        return search(tree[0])[0].chosen_child
    return temp_tree

def _get_human_move(tree): # Returns state
    # Handling EOFError for console input in a loop also means input
    # redirection with invalid input may cause an infinite loop, so input
    # redirection is not advised.
    try:
        move_str = input("Enter your move in the format row/column: ")
    except EOFError:
        return None

    # Format
    row_and_col = move_str.split("/")
    if len(row_and_col) != 2:
        return None # The next input prompt explains why this input failed

    # Type
    try:
        row, col = int(row_and_col[0]), int(row_and_col[1])
    except ValueError:
        print("Row and column values must be integers.")
        return None
    
    # Range
    if not (0 <= row < tree[0].height):
        print(f"Rows must be in [0, {tree[0].height-1}]")
        return None
    if not (0 <= col < tree[0].width):
        print(f"Columns must be in [0, {tree[0].width-1}]")
        return None
    
    # Only open squares
    move = tree[0].place(row, col)
    if move is None:
        print("Only open squares can be played.")
        return None
    
    return move # User has chosen a valid move

def _find_child(tree, state): # Returns node
    for ind in range(1, len(tree)):
        if state == tree[ind][0]:
            return tree[ind]
    
    return None

def _play_human_turn(tree): # Returns node
    # Get a valid move from the user (one must exist because tree[0].done is
    # guaranteed to be false at the start of the loop in play()).
    move_state = None
    while move_state is None:
        move_state = _get_human_move(tree)
    
    # Select the chosen move from the tree if it exists in the tree. Otherwise,
    # generate more of the tree, rooted at the chosen state.
    temp_tree = _find_child(tree, move_state)
    if temp_tree is None: # Parent was leaf or partially pruned.
        return [move_state] # On the AI's turn, it will generate more if needed
    return temp_tree # Requested node exists; advance to it.

def _format_action(action_tuple):
    return f'{action_tuple[0]}/{action_tuple[1]}'

def _show_move(tree, ai_turn):
    print(tree[0])
    print(f'{"AI" if ai_turn else "Human"} move:', _format_action(tree[0].action))
    print()

# The tree is traversed by two mechanisms:
#       1. tree[0].chosen_child
#           This retrieves the ObstructionBoard for the root (tree[0]) and then
#           the game tree list rooted at the game state the AI chooses in this
#           case. If not tree[0].done (which is guaranteed at the start of the
#           loop), a value of None for chosen_child indicates the tree has not
#           been sufficiently generated past this point due to depth limits or
#           pruning.
#       2. tree[x], for some 1 < x < len(tree) - 1
#           This retrieves a child node by its 1-based index (0 is the root
#           state). For the human turn, this occurs in _find_child(), where
#           None indicates that the state is not in the tree, and if
#           the state is known to be valid, the tree simply has not been
#           generated to this point.
def play(ai_first, search, first_tree):
    tree = first_tree
    ai_turn = ai_first
    ai_msg, human_msg = ("Player 1: AI", "Player 2: Human") if ai_first else \
                        ("Player 2: AI", "Player 1: Human")

    # Initial board state
    print("Board:")
    print(tree[0])
    print()

    # Continue taking turns until no open spaces remain. If the AI has no more
    # known moves and the game is not done, _play_ai_turn runs a search from
    # the current state.
    while not tree[0].done:
        if ai_turn:
            print(ai_msg)
            tree = _play_ai_turn(tree, search)
        else:
            print(human_msg)
            tree = _play_human_turn(tree)

        # Print the new board after this turn.
        _show_move(tree, ai_turn)
        ai_turn = not ai_turn
    
    print("Game complete.")
    print("Winner:", "Human" if ai_turn else "AI", f"({tree[0].winner})")

def main():
    try:
        ai_first, algorithm, algorithm_name, size, size_str = _parse_args()
    except (RuntimeError, ValueError) as e:
        print("Invalid input:", e)
        return -1
    
    start_state = ObstructionBoard.create(*size)
    if start_state is None:
        print("Program error: The game board could not be created.")
        return -1
    
    # Run the first search outside of play() so that the results can be printed
    # to the readme.
    tree, expanded_cnt = algorithm(start_state)
    _print_readme(size_str, algorithm_name, expanded_cnt)

    # Start the interactive console game. Discard expanded_cnt for new searches.
    play(ai_first, lambda state: algorithm(state)[0], tree)

if __name__ == "__main__":
    main()
