from Board import ObstructionBoard
from Solver import minimax, minimax_ab

tree, expanded = minimax_ab(ObstructionBoard.create(6, 6), 6)

print(expanded)
print(tree[0].chosen_child[0])
print(tree[0].chosen_child[0].action)
print(tree[0].utility)
print()

positive = []
negative = []
for node in tree:
    if isinstance(node, list):
        for node1 in tree:
            if isinstance(node1, list):
                for node2 in tree:
                    if isinstance(node2, list):
                        for node3 in tree:
                            if isinstance(node3, list):
                                pass
                            else:
                                (positive if node3.utility > 0 else negative).append(node3.utility)
                    else:
                        (positive if node2.utility > 0 else negative).append(node2.utility)
            else:
                (positive if node1.utility > 0 else negative).append(node1.utility)
    else:
        (positive if node.utility > 0 else negative).append(node.utility)

print(len(positive))
print(len(negative))
# board = ObstructionBoard.create(8, 7)
# board._tiles = [
#     [c for c in "O/O/O/X"],
#     [c for c in "///////"],
#     [c for c in "//////O"],
#     [c for c in "/X//X//"],
#     [c for c in "///////"],
#     [c for c in "X/O/O/X"],
#     [c for c in "///////"],
#     [c for c in "/X/----"],
# ]
# board._open_cnt = 4
# tree, expanded = minimax(board, 4)
# print(tree[0].utility)
# print(tree[0])
# print(tree[0].chosen_child[0])
# print(tree[0].chosen_child[0].chosen_child[0])