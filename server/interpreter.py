#!/usr/bin/env python3

import sys
from collections import deque
from copy import deepcopy
from pathlib import Path
import warnings
warnings.filterwarnings("ignore", category=SyntaxWarning)

def run_file(path: str) -> int:
    try:
        with open(path, "r") as f:
            file_contents = f.read()
        LexParse(file_contents.split())
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


state = "Start"
cval = 0
sym = {}
funcs = {}
execList = deque()
stmt = 0
debug = False
collecting = False
depth = -1
bodyStack = []
condStack = deque()
flagStack = deque()

root = Path(__file__).resolve().parent
stdlib_dir = root / "stdlib"
userlib_dir = root / "userlib"
pmo_files = [p.name for p in stdlib_dir.glob("*.pmo") if p.is_file()]
pmo_user_files = [p.name for p in userlib_dir.glob("*.pmo") if p.is_file()]
stdlib = [Path(fn).stem for fn in pmo_files]
userlib = [Path(fn).stem for fn in pmo_user_files]
deps = []


class Function:
    def __init__(self):
        self.contents = []
        self.params = []

    def do(self, args=None):
        global state
        local_sym = {}
        wait = []
        if args is None:
            args = []
        if len(args) != len(self.params):
            raise Exception(f"Args bad in function with params {self.params}")
        newContents = []
        for i in range(len(args)):
            if isinstance(args[i], int):
                args[i] = "tun " * (int(args[i]) + 1) + "sahur"
            elif isinstance(args[i], str):
                args[i] = "legit " + args[i] + " bro"
            elif isinstance(args[i], list):
                wait.append((i, args[i]))
                continue
            elif isinstance(args[i], float):
                args[i] = "tf legit " + str(args[i]) + " bro"
            elif args[i]:
                args[i] = "sigma"
            elif not args[i]:
                args[i] = "beta"
            local_sym[self.params[i]] = args[i]
            t = f"ts rizz {self.params[i]} {args[i]} pmo"
            for c in t.split():
                newContents.append(c)
        for t in wait:
            local_sym[self.params[t[0]]] = t[1]
        for c in self.contents:
            newContents.append(c)
        # print(newContents)
        state = "Start"
        res = LexParse(contents=newContents, lexto=deque(), loc=local_sym)
        state = "End"
        return res


reserved = {"ts", "pmo", "rizz", "tun", "sahur", "sigma", "beta", "touch", "#shrink", "cavendish", "big25", "crockpot",
            "chill", "grind", "L", "+", "-", "*", "/", "%", "or", "and", "not", "print", "yap", "set", "mogs", "vibes",
            "hawk", "if", "lion", "then", "tiger", "else", "fr", "ong", "yo", "kid", "gurt", "legit", "bro", "sayong",
            "spill", "chat?", "cond", "sybau", "GOAT", "LEBRON", "ngl", "legoat", "dih", "REF", "DO", "SOMETHING",
            "stroke", "lowkey", "tf", "->", "<-", "bigf", "./", "ls", "gt", "ad", "rm", "[]", "get", "add", "remove",
            "pt", "put", "girth", "BOOM", "len", "ret"}


def LexParse(contents, lexto=execList, loc=None):
    global state
    global cval
    global bodyStack
    global collecting
    global depth
    prestate = None
    i = 0
    r = None
    while i < len(contents):
        if debug:
            print("exec", lexto)
            print('state', state)
            # print("flags", flagStack)
        c = contents[i]
        if c == "->":
            prestate = state
            state = "Comment"
            i += 1
            c = contents[i]
        elif state == "Start":
            if c == "ts":
                state = "ts"
            elif c == "LEBRON":
                i += 1
                c = contents[i]
                temp = Function()
                funcs[c] = temp
                i += 1
                c = contents[i]
                while c != "ngl":
                    temp.params.append(c)
                    i += 1
                    c = contents[i]
                i += 1
                c = contents[i]
                while c != "GOAT":
                    temp.contents.append(c)
                    i += 1
                    c = contents[i]

            elif c == "REF":
                i += 1
                c = contents[i]
                while c != "DO":
                    if "," in c:
                        c = c.replace(",", "")
                    deps.append(c)
                    i += 1
                    c = contents[i]
                i += 1
                c = contents[i]
                if c != "SOMETHING":
                    raise Exception(f"Failed to correctly import modules. Are you closing with DO SOMETHING?")
                for j in deps:
                    if j in stdlib:
                        with open("stdlib/" + j + ".pmo") as file:
                            LexParse(file.read().split())
                    elif j in userlib:
                        with open("/userlib/" + j + "pmo") as file:
                            LexParse(file.read().split())
                    else:
                        raise Exception(f"Failed to load module {j}. It is either missing from the stdlib, or you"
                                        f" forgot to add it to userlib.")
            else:
                raise Exception(f"Commands must start with ts or LEBRON stmt{stmt + 1}")

        elif state == "ts":
            if c == "yap":
                state = "E"
                lexto.append("print")

            elif c == "rizz":
                state = "ID"

            elif c == "sybau":
                state = "E"

            elif c == "hawk":
                state = "E"
                lexto.append("check")

            elif c == "lion":
                if debug:
                    print("lion", flagStack[-1])
                if not flagStack[-1]:
                    state = "skip"
                else:
                    state = "End"

            elif c == "tiger":
                if debug:
                    print("tiger", flagStack[-1])
                if flagStack[-1]:
                    state = "skip"
                else:
                    state = "End"

            elif c == "fr":
                state = "End"

            elif c == "ong":
                flagStack.pop()
                state = "End"

            elif c == "pt":
                lexto.append("put")
                state = "E"

            elif c == "dih":
                lexto.append("setReturn")
                state = "E"

            elif c == "kid":
                i += 1
                c = contents[i]
                if c != "pmo":
                    raise Exception(f"Pmo expected stmt {stmt + 1}")
                depth += 1
                myDepth = depth
                bodyStack.append([])
                i += 1
                c = contents[i]
                level = 1
                while True:
                    if c == "kid":
                        level += 1
                    elif c == "gurt":
                        level -= 1
                        if level == 0:
                            break
                    bodyStack[myDepth].append(c)
                    i += 1
                    c = contents[i]
                bodyStack[myDepth].pop(-1)
                state = "Start"
                while execute(deepcopy(condStack[myDepth]), loc=loc):
                    LexParse(deepcopy(bodyStack[myDepth]), loc=loc, lexto=deque())
                depth -= 1
                bodyStack.pop(myDepth)
                i += 1
                c = contents[i]
                if c != "pmo":
                    raise Exception(f"Pmo expected stmt {stmt + 1}")
                i += 1
                continue

            else:
                raise Exception(f"Assignment or Function Expected stmt {stmt + 1} {c}")

        elif state == "ID":
            if c in reserved:
                raise Exception(f"{c} is reserved by the language stmt {stmt + 1}")
            else:
                lexto.append(c)
                lexto.append("set")
                state = "E"

        elif state == "E":
            if c == "touch":
                lexto.append("+")

            elif c == "#shrink":
                lexto.append("-")

            elif c == "cavendish":
                lexto.append("*")

            elif c == "big25":
                lexto.append("/")

            elif c == "bigf":
                lexto.append("./")

            elif c == "crockpot":
                lexto.append("%")

            elif c == "mogs":
                lexto.append(">")

            elif c == "vibes":
                lexto.append("==")

            elif c == "chill":
                lexto.append("or")

            elif c == "grind":
                lexto.append("and")

            elif c == "L":
                lexto.append("not")

            elif c == "stroke":
                lexto.append("concat")

            elif c == "sayong":
                lexto.append("tobool")

            elif c == "spill":
                lexto.append("toint")

            elif c == "lowkey":
                lexto.append("tostring")

            elif c == "tf":
                lexto.append("tofloat")

            elif c == "tun":
                cval = 0
                state = "tun"

            elif c == "legit":
                cval = ""
                state = "legit"

            elif c == "chat?":
                lexto.append("input")

            elif c == "sigma":
                lexto.append(True)
                state = "End"

            elif c == "beta":
                lexto.append(False)
                state = "End"

            elif c == "ls":
                lexto.append([])
                state = "End"

            elif c == "ad":
                lexto.append("add")

            elif c == "gt":
                lexto.append("get")

            elif c == "rm":
                lexto.append("remove")

            elif c == "BOOM":
                lexto.append("split")

            elif c == "girth":
                lexto.append("len")

            elif c in sym:
                lexto.append(c)
                state = "End"

            elif loc is not None and c in loc:
                lexto.append(c)
                state = "End"

            elif c in funcs:
                a = c
                argc = len(funcs[c].params)
                while argc:
                    i += 1
                    c = contents[i]
                    a += " " + c
                    argc -= 1
                lexto.append(a)
                state = "End"

            else:
                raise Exception(f"Not a valid Expression stmt {stmt + 1} {c}")

        elif state == "tun":
            if c == "tun":
                cval += 1

            elif c == "sahur":
                lexto.append(cval)
                state = "End"

            else:
                raise Exception(f"Int Interrupt stmt {stmt + 1}")

        elif state == "legit":
            if c == "bro":
                if cval != "":
                    cval = cval[:len(cval) - 1]
                lexto.append(cval)
                lexto.append("Str")
                state = "End"
            else:
                cval += c + " "

        elif state == "End":
            if c == "yo":
                lexto.append("cond")

            elif c == "pmo":
                m = execute(lexto, loc)
                if m is not None:
                    r = m
                state = "Start"

            else:
                state = "E"
                i -= 1

        elif state == "skip":
            if debug:
                print("Skipping")
            while c != "fr":
                i += 1
                c = contents[i]
            state = "End"

        elif state == "Comment":
            while c != "<-":
                i += 1
                c = contents[i]
            state = prestate
            prestate = None

        i += 1
    return r


def trans(value):
    if isinstance(value, bool) and not (value is 1 or value is 0):
        return "sigma" if value else "beta"
    elif isinstance(value, int):
        return (value + 1) * "tun " + "sahur"
    elif isinstance(value, str):
        return "legit " + value + " bro"
    elif isinstance(value, float):
        return "ts tf " + str(value)
    elif isinstance(value, list):
        return "ls " + str(value)


def execute(execL=execList, loc=None):
    global stmt
    global flagStack
    global collecting
    if debug:
        print("Conds", condStack)
        print(sym)
        print(loc)
    flag = None
    if execL == execList:
        stmt += 1
    temp = None
    setting = False
    literal = False
    ret = None
    nxt = deque()
    while execL:
        if debug:
            print(execL)
            print(nxt)
            print(temp)
            print()
        e = execL.pop()
        if literal:
            if temp is None:
                temp = e
            else:
                nxt.append(e)
            literal = False
        elif isinstance(e, bool) and not (e is 1 or e is 0):
            if temp is None:
                temp = e
            else:
                nxt.append(e)
        elif isinstance(e, int):
            if temp is None:
                temp = e
            else:
                nxt.append(e)
        elif isinstance(e, float):
            if temp is None:
                temp = e
            else:
                nxt.append(e)
        elif isinstance(e, list):
            if temp is None:
                temp = e
            else:
                nxt.append(e)
        elif e == "+":
            if len(nxt) > 1:
                nxt.append(nxt.pop() + nxt.pop())
            else:
                temp += nxt.pop()
        elif e == "-":
            if len(nxt) > 1:
                nxt.append(nxt.pop()-nxt.pop())
            else:
                temp = nxt.pop() - temp
        elif e == "*":
            if len(nxt) > 1:
                nxt.append(nxt.pop() * nxt.pop())
            else:
                temp = nxt.pop() * temp
        elif e == "/":
            if len(nxt) > 1:
                nxt.append(nxt.pop() // nxt.pop())
            else:
                temp = nxt.pop() // temp
        elif e == "./":
            if len(nxt) > 1:
                nxt.append(nxt.pop() / nxt.pop())
            else:
                temp = nxt.pop() / temp
        elif e == "%":
            if len(nxt) > 1:
                nxt.append(nxt.pop() % nxt.pop())
            else:
                temp = nxt.pop() % temp
        elif e == ">":
            if len(nxt) > 1:
                nxt.append(nxt.pop() > nxt.pop())
            else:
                temp = nxt.pop() > temp
        elif e == "==":
            if len(nxt) > 1:
                nxt.append(nxt.pop() == nxt.pop())
            else:
                temp = nxt.pop() == temp
        elif e == "or":
            if len(nxt) > 1:
                nxt.append(nxt.pop() or nxt.pop())
            else:
                temp = nxt.pop() or temp
        elif e == "and":
            if len(nxt) > 1:
                nxt.append(nxt.pop() and nxt.pop())
            else:
                temp = nxt.pop() and temp
        elif e == "not":
            if nxt:
                nxt[-1] = not nxt[-1]
            else:
                temp = not temp
        elif e == "concat":
            if len(nxt) > 1:
                tmp = nxt.pop()
                nxt.append(nxt.pop() + tmp)
            else:
                temp = nxt.pop() + temp
        elif e == "add":
            if len(nxt) > 1:
                nxt.append(nxt.pop().append(nxt.pop()))
            else:
                temp = nxt.pop().append(temp)
        elif e == "get":
            if len(nxt) > 1:
                nxt.append(nxt.pop()[nxt.pop()])
            else:
                temp = nxt.pop()[temp]
        elif e == "remove":
            if nxt:
                nxt[-1].pop(-1)
            else:
                temp.pop(-1)

        elif e == "tobool":
            if nxt:
                nxt[-1] = bool(nxt[-1])
            else:
                temp = bool(temp)
        elif e == "toint":
            if nxt:
                nxt[-1] = int(nxt[-1])
            else:
                temp = int(temp)
        elif e == "tostring":
            if nxt:
                nxt[-1] = str(nxt[-1])
            else:
                temp = str(temp)
        elif e == "tofloat":
            if nxt:
                nxt[-1] = float(nxt[-1])
            else:
                temp = float(temp)
        elif e == "put":
            if len(nxt) != 2:
                raise Exception("Incorrect array put")
            arr = nxt.pop()
            ind = nxt.pop()
            arr[ind] = temp
        elif e == "split":
            if nxt:
                nxt[-1] = nxt[-1].split()
            else:
                temp = temp.split()
        elif e == "len":
            if nxt:
                nxt[-1] = len(nxt[-1])
            else:
                temp = len(temp)
        elif e == "print":
            print(trans(temp), f"({temp})")
        elif e == "check":
            flag = bool(temp)
        elif e == "cond":
            condStack.append(deque([deepcopy(i) for i in execL]))
        elif e == "collect":
            collecting = True
        elif e == "clear":
            temp = None
        elif e == "input":
            execL.append(input(temp))
            execL.append("Str")
        elif e == "Str":
            literal = True
        elif e == "set":
            setting = True
        elif e == "setReturn":
            ret = temp
        else:
            parts = e.split()
            if parts[0] in funcs:
                fname = parts[0]
                rawArgs = parts[1:]
                resolved = []
                for a in rawArgs:
                    if isinstance(a, (int, bool)):
                        resolved.append(a)
                    elif isinstance(a, str) and a.isdigit():
                        resolved.append(int(a))
                    elif loc is not None and a in loc:
                        resolved.append(loc[a])
                    elif a in sym:
                        resolved.append(sym[a])
                    else:
                        raise Exception(f"Unknown argument {a!r} for function {fname}")
                res = funcs[fname].do(args=resolved)
                if res is not None:
                    execL.append(res)
                    if isinstance(res, str):
                        execL.append("Str")
            elif setting:
                if loc is not None:
                    loc[e] = temp
                else:
                    sym[e] = temp
                setting = False
            else:
                value = loc[e] if (loc is not None and e in loc) else sym[e]
                if value is None:
                    print(f"about to append None for variable {e!r}")
                execL.append(value)
                if isinstance(value, str):
                    execL.append("Str")
    if flag is not None:
        flagStack.append(flag)
    return ret


def main():
    if len(sys.argv) != 2:
        print("Usage: interpreter.py <script.tspmo>", file=sys.stderr)
        sys.exit(1)

    script_path = sys.argv[1]
    exit_code   = run_file(script_path)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()