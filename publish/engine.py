import pickle;
import base64;
from dill.source import getsource;
import sys;


class Engine:
    def r(self, name, *args):
        uName = name if isinstance(name, str) else name.__name__;

        fixIndent = self.funs[uName].split("    ");
        newFun = "";
        count = -1
        for i in fixIndent:
            count += 1;
            newFun += f"    {i}" if count > 1 else i;

        argument = "";
        for i in args:
            argument += f", {i}" if not isinstance(i, str) else f", \"{i}\"";

        statement = f"{newFun}\n\n{uName}(this{argument});";
        exec(statement, globals().update({"this": self}));
        return_ = self.return_;
        self.return_ = None;
        return return_;

    '''Function Redirects'''

    def run(self): return self.r("run");
    def test(self, a): return self.r("test", a);
    def export(self): return self.r("export");
    def setBasicData(self): return self.r("setBasicData");

class Error(Exception):
    def __init__(self, type, msg=None) -> None:
        self.type = type;
        self.error = msg;

    def __repr__(self) -> str:
        return f"{self.type}Error: [{self.error}]" if self.error else f"{self.type}Error";

class Loc:
    def __init__(self, name, value=None, children=None) -> None:
        self.name = name;
        self.children = children if children else [];
        self.value = value;

    def search(self, names):
        nameList = names if isinstance(names, list) else list(names);
        if nameList[0] != self.name: return None;
        nameList.pop(0);
        if len(nameList) < 1: return self;

        for i in self.children:
            candidate = i.search(nameList);
            if candidate: return candidate;

    def append(self, names, loc):
        pointer = 0;
        searchList = [self]; searchList.extend(Loc(a) for a in names); searchList.append(loc);
        index = -1;
        for i in searchList:
            index += 1;
            pointer = index;
            parent = None;

            def pfind(point, search):
                out = [];
                for i in search:
                    out.append(i.name);
                    if i == search[point]:
                        break;
                return out;

            while not parent:
                parent = self.search(pfind(pointer, searchList));
                if not parent: pointer -= 1;

            if index + 1 != len(searchList):
                pointer += 1;
                parent.children.append(searchList[pointer]);

        return self;

    def new(self, name, value=None, children=[]):
        return Loc(name, value, children);

    def rep(self, iter):
        final = ("\t" * iter) + "[" + str(self.name) + "]" + (f" -> {type(self.value)}" if self.value else "") + ":\n";
        for i in self.children:
            final += i.rep(iter + 1);
        return final;

    def __repr__(self) -> str:
        return self.name;

class Memory:
    def __init__(self, log, locs=[Loc(0)]) -> None:
        '''Instance Varibles'''
        self.log = log;
        self.error = None;
        self.result = None;
        '''LT Varibles'''
        self.locs = locs;

    def register(self, res):
        if isinstance(res, Memory):
            self.error = res.error;
            return res.result;

    def failure(self, other):
        if isinstance(other, Error) and not self.error:
            self.error = other;
            return self;

    def output(self, other):
        self.result = other;
        return self;

    def search(self, slot, *names):
        self.refresh();
        try: stem = self.locs[slot];
        except: raise Error("Memory", f"Cannot access slot '{slot}' in memory locations");
        dirc = [slot]; dirc.extend(names);
        return stem.search(dirc);

    def refresh(self):
        try: self.locs = pickle.loads(base64.b85decode(open("Memory.rot", "rb").read()));
        except: pass;

    def commit(self, slot, dirc, loc):
        self.refresh();
        try: stem = self.locs[slot];
        except: raise Error("Memory", f"Cannot access slot '{slot}' in memory locations");
        stem.append(dirc, loc);
        open("Memory.rot", "w").write(base64.b85encode(pickle.dumps(self.locs)).decode());

        # self.log(f"Successfully commited memory at loc {dirc.append(loc.name)}");

        return self;

    def copy(self):
        return Memory(self.log, self.locs);

    def new(self, log, locs=[Loc(0)]):
        return Memory(log, locs);
