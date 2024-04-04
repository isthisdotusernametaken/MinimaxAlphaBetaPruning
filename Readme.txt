Evaluation Function:
    The goal of the function is to choose the state that leaves the fewest
    remaining squares for the opponent or the most remaining squares for
    yourself. However, any state that leaves exactly 1 square for the opponent
    should be avoided if a better option exists (i.e., if there is a state with
    0 open squares or more than 1 open square), as such a state would be a
    guaranteed win for the opponent; because the resulting utility value will
    be strongly not preferred by the player who makes the choice (MAX/MIN), it
    will necessarily be strongly preferred by the other player (MIN/MAX).
    

    The utility of a non-terminal leaf node is as follows (where c is the the number of open squares):
        if MAX will choose/not choose this node // i.e., this node is at a MIN level
            if c is exactly 1
                return -(width * height + 1) // which is less than all potential c
            else // so c > 1
                return -c
        else // so MIN will choose/not choose this node (i.e., this node is at a MAX level)
            if c is exactly 1
                return width * height + 1 // which is greater than all potential c
            else // so c > 1
                return c
    
    This is implemented in _evaluate_node(board) near the top of Board.py.


    A necessary side effect of choosing based on non-terminal leaves' utility
    - while considering who has the current turn - is that the lookahead depth
    will determine whether both players base their decisions on
    seeking/avoiding MAX's preferences or on avoiding/seeking MIN's
    preferences. In this case, the result is that odd depths lead to MAX
    minimizing MIN's options at a max-depth state while MIN maximizes its
    max-depth options, whereas even depths lead to MIN minimizing MAX's options
    at a max-depth state while MAX maximizes its max-depth options.
    To achieve symmetric behavior for two AI players while sacrificing
    strategicness, a lookahead depth of 1 can be used. 

    Note that, because MAX's choices will be among nodes with negative c,
    smaller-magnitude values of c (fewer open squares for the next MIN turn)
    will be preferred by MAX and avoided by MIN. Also, because MIN's choices
    will be among nodes with positive c, smaller-magnitude values of c (fewer
    open squares for the next MAX turn) will be preferred by MIN and avoided by
    MAX.
    Additionally, because all non-terminal leaf nodes are at the same depth as
    each other, utility values coming from non-terminal leaf nodes backed-up in
    the search will always be either all positive or all negative, so the fact
    that MAX's choices among non-terminal leaves have negative utility while
    MIN's have positive utility will not at all affect the choices in the
    search. I have experimentally confirmed this by grouping all utilities into
    positive and negative lists for given depths, and odd depths starting with
    MAX with no terminal states give negative utility for all nodes, while even
    depths starting with MAX and no terminal states give positive utility for
    all nodes.
    This implementation is preferred for the simplicity of calculation
    while not affecting the search outcome, but it could be modified so that
    MIN's choices among leaves are negative and become more negative as c
    decreases while MAX's choices are positive and become more positive as c
    decreases (by subtracting c from the total square count before the possible
    negation of the result).


All tests below are for the AI playing first (i.e., with no arbitary human
moves before the search).

********************
Size: 6*6
Algorithm: MM
Expanded: 24597
Depth: 3

Size: 6*6
Algorithm: MM
Expanded: 428613
Depth: 4

Size: 6*6
Algorithm: AB
Expanded: 1411
Depth: 3

Size: 6*6
Algorithm: AB
Expanded: 21350
Depth: 4

********************
Size: 6*7
Algorithm: MM
Expanded: 42735
Depth: 3

Size: 6*7
Algorithm: MM
Expanded: 968223
Depth: 4

Size: 6*7
Algorithm: AB
Expanded: 1877
Depth: 3

Size: 6*7
Algorithm: AB
Expanded: 25716
Depth: 4

********************
Size: 7*8
Algorithm: MM
Expanded: 115875
Depth: 3

Size: 7*8
Algorithm: MM
Expanded: 4101459
Depth: 4

Size: 7*8
Algorithm: AB
Expanded: 3261
Depth: 3

Size: 7*8
Algorithm: AB
Expanded: 41205
Depth: 4

********************
Size: 8*8
Algorithm: MM
Expanded: 181925
Depth: 3

Size: 8*8
Algorithm: MM
Expanded: 7801229       Note: The program exceeded 10GB of RAM usage and VSCode started to glitch while some other programs crashed, so I am unsure of the accuracy of this value.
Depth: 4

Size: 8*8
Algorithm: AB
Expanded: 4245
Depth: 3

Size: 8*8
Algorithm: AB
Expanded: 54705
Depth: 4

