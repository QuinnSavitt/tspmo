# tspmo README

# 1) Language Basics

## 1.1) Statement Format

    All statements (aside from function definitions) must start with `ts` and end with `pmo`. The expressions inside must resolve to a primary operator (See Section 1.3.1).

## 1.2) Basic Types

### 1.2.1) Integers

    Integer literals are defined by repeated `tun`s followed by a closing `sahur`. The value is defined as the number of `tun`s minus 1.

EX 1.1:

```
tun tun tun tun tun sahur -> 4 <-
tun sahur -> 0 <-

```

### 1.2.2) Booleans

    Boolean literals are defined as the following mapping: `sigma`->True `beta`->False.

### 1.2.3) Strings

    String literals are opened by `legit` and closed by `bro`.

```
legit Hello World bro -> "Hello World" <-
```

### 1.2.4) Floats

    You cannot create float literals directly, but through `bigf` divisions and `tf` conversions.

### 1.2.5) Lists

    Lists cannot be initialized containing data, but can be initialized empty using `ls`

## 1.3) Operators

### 1.3.1) Primary Operators

    Primary operators are required to be the first token after `ts` , and all statements will evaluate down to one of the following.

### 1.3.2) `rizz` [id] [expr]

    Assigns the result of <expr> to <id>.

```
ts rizz x tun tun tun sahur pmo -> assign value 2 to x <-
```

### 1.3.3) `yap` [expr]

    Prints the result of <expr>.

### 1.3.4) `sybau` [expr]

    NoOp. Useful for in-place expressions.

### 1.3.5) `dih` [expr]

    Sets return value of the current function with the value of <expr>.

### 1.3.6) Additional Primary Operators

    Some primary operators are a bit more complex and are placed in following sections.

### 1.3.7) Secondary Operators

    Secondary operators are responsible for higher level processes. They can appear anywhere in statements.

### 1.3.8) `chat?` [prompt: str] → str

    Requests user input with <prompt>. Returns the string input of the user.

```
ts rizz x chat? legit What's your name? bro pmo -> assign user input to x <-
```

### 1.3.9) `spill` [expr] → int

   Converts from expr to integer.

### 1.3.10) `sayong` [expr] → bool

    Converts from expr to boolean.

### 1.3.11) `tf` [expr] → float

    Converts from expr to float.

### 1.3.12) `lowkey` [expr] → str

    Converts from expr to string.

### 1.3.13) Arithmetic Operators

   Operators involving two integer expressions evaluating to an int.

### 1.3.14) `touch` [a: int, float] [b: int, float] → int, float

    Returns a + b.

### 1.3.15) `#shrink` [a: int, float] [b: int, float] → int, float

    Returns a - b.

### 1.3.16) `cavendish` [a: int, float] [b: int, float] → int, float

    Returns a * b.

### 1.3.17) `big25` [a: int, float] [b: int, float] → int

    Returns a / b (integer division).

### 1.3.18) `crockpot` [a: int, float] [b: int, float] → int, float

    Returns a % b (remainder operator).

### 1.3.19) `bigf` [a: int, float] [b: int, float] → float

    Returns a / b (float division)

### 1.3.20) Boolean Operators

    Operations involving ≤ 2 boolean expressions.

### 1.3.21) `chill` [a: bool] [b: bool] → bool

    Returns a or b (a || b).

### 1.3.22) `grind` [a: bool] [b: bool] → bool

    Returns a and b (a && b).

### 1.3.23) `L` [a: bool] → bool

    Returns not a (! a).

### 1.3.24) Comparison Operators

   Operations involving the comparison of two integers, returning a boolean.

### 1.3.25) `mogs` [a: int, float] [b: int, float] → bool

    Returns a > b.

### 1.3.26) `vibes` [a: any] [b: any] → bool

    Returns a == b.

### 1.3.27) String Operations

### 1.3.28) `stroke` [a: str] [b: str] → str

    Concatenates a and b.

### 1.3.29) `BOOM` [a: str] → list

     Splits a by whitespace.

### 1.3.30) List Operations

### 1.3.31) `ad` [a: list] [b: any] → list

     Appends b to a. Works in-place.

### 1.3.32) `rm` [a: list]

     Removes the last item of a (does not return it).

### 1.3.33) `pt` [a: list] [b: int] [c: any]

     Sets index b of list a to value c. Must be in-place. Note: this is a primary operator.

### 1.3.34) `gt` [a: list] [b: int] → any

     Gets the item in list a at index b.

### 1.3.35) `girth` [a: list, str] → int

     Returns the length of a.

## 1.4) Control Flow

### 1.4.1) Conditionals

### 1.4.2) Flags

    Flags are precomputed values that determine whether conditional branches fire or not. They are internally represented by the “flag stack”.

### 1.4.3) `hawk` [expr: bool]

    Pushes the result of [expr] onto the flag stack. Note: this is a primary operator.

```
ts hawk mogs tun tun tun sahur tun tun sahur pmo -> evaluates to sigma (True), <-
                                                 -> pushes sigma to flagstack. <-
```

### 1.4.4) `lion`

    Fires conditional branch if the top of the flag stack is True. Note: this is a primary operator.

### 1.4.5) `tiger`

    Fires conditional branch if the top of the flag stack is False. Note: this is a primary operator.

### 1.4.6) `fr`

    Closes conditional branch. Note: this is a primary operator.

### 1.4.7) `ong`

    Pops the top of the flag stack. Note: this is a primary operator.

### 1.4.8) Loops

### 1.4.9) Conditions

    Conditions are similar to flags in that they are a stacked structure that determines if a branch is fired, however these are computed each time they are checked. This is useful for bounding loops.

### 1.4.10) [expr] `yo`

   A keyword that saves <expr> as a condition.

```
ts sybau mogs x i yo pmo -> adds a condition [mogs x i yo] <-
```

### 1.4.11) `kid`

    Launch a loop bounded by the condition at the top of the stack. Note: this is a primary operator.

### 1.4.12) `gurt`

    Close a loop, check the condition. Note: this is a primary operator.

## 1.5) Modules

### 1.5.1) Importing

    Importing modules is possible through the `REF` … `DO SOMETHING` statement. Modules are importable from the same file directory, or from the standard library, and are seperated by commas.

```
REF stdlib, hello_world, hi DO SOMETHING -> imports three modules <-
```

## 1.6) Functions

### 1.6.1) Function Declaration

    Function declaration should take the format: `LEBRON` [arg]* `ngl` where the * represents 0 or more arguments. They are then followed by commands, and closed by `GOAT`.

### 1.6.2) Function Calling

    Calling a function follows the format: [fname] [arg]*. Functions cannot be used as primary operators.

### 1.6.3) Function Arguments

    Arguments **must** be previously defined variables.

## 1.7) Comments

Comments are declared using `->` to open and `<-` to close.

## 1.8) Sample File

   Below is a sample file with comments.

```
LEBRON fib n ngl                                      -> declare function fib <-
	ts hawk mogs n tun tun sahur pmo                    -> check if n > 1 <-
	ts lion pmo                                         -> if True <-
		ts rizz a #shrink n tun tun sahur pmo             -> set a to n - 1 <-
		ts rizz b #shrink n tun tun tun sahur pmo         -> set b to n - 2 <-
		ts rizz c fib a pmo                               -> set c to fib a <-
		ts rizz d fib b pmo                               -> set d to fib b <-
		ts dih touch c d pmo                              -> return c + b <-
	ts fr pmo                                           -> close branch <-
	ts tiger pmo                                        -> if False <-
		ts dih tun tun sahur pmo                          -> return 1 <-
	ts fr pmo                                           -> close branch <-
	ts ong pmo                                          -> pop flag <-
GOAT                                                  -> close function declaration <-

ts rizz x spill chat? legit How many? bro pmo         -> x = user input for loop length <-
ts rizz i tun sahur pmo                               -> initialize i = 0 <-
ts dih mogs x i yo pmo                                -> while i < x <-
ts kid pmo                                            -> open loop <-
	ts yap fib i pmo                                    -> print fib i <-
	ts rizz i touch i tun tun sahur pmo                 -> i = i + 1 <-
ts gurt pmo                                           -> close loop <-
```