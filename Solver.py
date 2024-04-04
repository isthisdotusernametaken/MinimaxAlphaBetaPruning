# Note: Instead of generating the entire tree down to the specified depth and
# then searching, this module generates the tree while searching. This does not
# allow sorting for Alpha-Beta Pruning, but it does prevent pruned branches
# from being generated in the first place.

from math import inf


# Node management during search

# The data for a given node in MM search. This is not included in the game tree
# itself and is discarded when the search finishes this subtree.
class MMData:
    def __init__(self, depth):
        self.depth = depth
    
    def child(self): # Decrease the remaining depth for the child
        return MMData(self.depth - 1)
    
    def update_alpha(self, _): # MM has no alpha
        pass

    def update_beta(self, _): # MM has no beta
        pass

    def prune(self): # No pruning for MM
        return False

# The data for a given node in AB search
class ABData:
    def __init__(self, depth, alpha, beta):
        self.depth = depth
        self.alpha = alpha
        self.beta = beta

    def child(self): # Decrease the remaining depth and keep alpha and beta
        return ABData(self.depth - 1, self.alpha, self.beta)

    def update_alpha(self, new_utility): # Update alpha if larger value found
        if new_utility > self.alpha:
            self.alpha = new_utility

    def update_beta(self, new_utility): # Update beta if smaller value found
        if new_utility < self.beta:
            self.beta = new_utility

    def prune(self): # Prune if alpha and beta cross
        return self.alpha >= self.beta


# Search algorithms

# Explanation of node_data:
#       node_data is an instance of either MMData or ABData from the top of
#           this file.
#       None of the data in a child's node_data is read by the parent (i.e., it
#           is only passed down the tree). 
#       For Minimax, node_data contains only the depth/number of remaining
#           turns along the path. For Minimax with Alpha-Beta Pruning,
#           node_data contains the depth and the alpha and beta values from the
#           parent and may be updated while the current call is running.
#       node_data also includes the child() method to copy itself for recursive
#           calls and the update_alpha(), update_beta(), and prune() methods
#           for optional pruning functionality. Since child() returns an
#           instance of the same class, the original pruning methods are
#           propagated to the recursive calls.
def _base_minimax(state, node_data):
    node = [state]
    total_expanded = 1 # Count each new state as an expanded node

    # If the state's children should be evaluated...
    if node_data.depth != 0 and not state.done:
        # Choose the max child and (for AB) update alpha for MAX; choose the
        # min child and (for AB) update beta for MIN.
        state.utility, max_or_min, update_ab = \
            (-inf, max, node_data.update_alpha) if state.MAX_turn else \
            (inf, min, node_data.update_beta)

        # For each valid move, repeat this algorithm for the resulting child,
        # add the produced tree as a subtree, and tally the number of expanded
        # nodes.
        # If the rest of the branches should be pruned, both loops exit.
        for i in range(state.height):
            for j in range(state.width):
                new_state = state.place(i, j)

                if new_state is not None:
                    # Repeat the algorithm for the child.
                    # If depth reaches 0 or new_state is a terminal node, this
                    # code will not run for the child, so the child's utility
                    # will be automatically generated with terminal utility or
                    # with the evaluation function. Otherwise, this code in the
                    # recursive call will determine the child's utility based
                    # on its own children.
                    child, expanded = _base_minimax(new_state, node_data.child())
                    node.append(child)
                    total_expanded += expanded

                    # If a new max/min is found (or no states have been checked
                    # yet), update the utility and possibly alpha or beta.
                    temp = max_or_min(state.utility, new_state.utility)
                    if temp != state.utility or state.chosen_child is None:
                        state.chosen_child = child # Track the AI's choice
                        state.utility = temp # New max/min

                        update_ab(temp) # Possible new alpha/beta (update node_state)
                        if (node_data.prune()): # Prune if alpha >= beta for AB
                            # If the AI's choice does not lead to a terminal
                            # state, the AI is not guaranteed to choose the
                            # child with the best utility if the human's
                            # choices lead here because not all children were
                            # evaluated. This requires running the search again
                            # to stay true to the heuristic.
                            #
                            # Pruning can occur at the root node only if a win
                            # state is found (since alpha and beta start at
                            # +-infinity), so chosen_child is not reset to None
                            # in these cases to ensure chosen_child is never
                            # None for the root when there is a legal move
                            # (i.e., if the root is not a terminal state).
                            if state.utility not in (inf, -inf):
                                state.chosen_child = None # Signal new search needed
                            break
            else: # Not pruned yet: continue expanding (skip the break statement)
                continue

            break # Pruned: exit both loops immediately

    return node, total_expanded

def minimax(state, depth):
    return _base_minimax(state, MMData(depth))

def minimax_ab(state, depth):
    # Alpha starts at -inf; beta starts at inf
    return _base_minimax(state, ABData(depth, -inf, inf))