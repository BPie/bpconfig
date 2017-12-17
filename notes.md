# workflow

- print
    - clear
    - print header
    - print current
    - print footer

- gather input
    - spc <-- timeout, key_enter, key_escape
    - inp <-- one char at a time

- handle input
    - ??


# members
- _pos: list of names from root to current cell
- _t: terminal instance
- _inp: normal input
- _spc: special input (timeout, keys)
- _loc_cache: coursor location dictionary
- _actions: map input --> action for that input
- _current: current cell
- _state: current state (enum, property, contaienr)
- _parent: parent of current cell
- _get_styled_attr
- _formated_cell_attr
