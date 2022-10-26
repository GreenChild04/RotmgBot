import pickle;
import base64;
from dill.source import getsource;
import sys;


class Error:
    def __init__(self, type, msg=None):
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


'''Classes'''
class TestClass:
    def __init__(self, engine, data) -> None:
        self.data = data;
        self.engine = engine;

    def run(self):
        print(f"Engine is working! Success: [{self.data}]");

class Memory:
    def __init__(self, this, log, locs=[Loc(0)]) -> None:
        '''Instance Varibles'''
        self.log = log;
        self.error = None;
        self.result = None;
        self.this = this;
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
        return Memory(self.this, self.log, self.locs);

    def new(self, this, log, locs=[Loc(0)]):
        return Memory(this, log, locs);


'''Engine'''
class Engine:
    def __init__(self) -> None:
        '''Internal Varibles'''
        self.version = "0.1.7";
        '''Function Instances'''
        self.objs = self.getObjs();
        '''Imports'''
        self.loc = Loc("Vital");

    '''Anti Piracy Stuff'''

    def getObjs(self):
        oldFuns = [self.run, self.export, self.test, self.setBasicData, TestClass, Memory];
        objs = {};

        for i in oldFuns:
            objs[i.__name__] = getsource(i);

        return objs;

    def r(self, name, *args):
        uName = name if isinstance(name, str) else name.__name__;
        class Result:
            def __init__(self) -> None:
                self.result = None;
            def return_(self, result):
                self.result = result;

        return_ = Result();

        fixIndent = self.objs[uName].split("    ");
        newFun = "";
        count = -1
        for i in fixIndent:
            count += 1;
            newFun += f"    {i}" if count > 1 else i;

        argument = "";
        argDict = {};
        count = -1;
        for i in args:
            count += 1;
            key = f"___{count}Object";
            argDict[key] = i;
            argument += f", {key}";

        statement = f"{newFun}\n\nReturn({uName}(this{argument}));";
        lib = globals(); lib.update({"this": self, "Return": return_.return_}); lib.update(argDict);
        exec(statement, lib);
        return return_.result;

    def c(self, name, *args):
        class Result:
            def __init__(self) -> None:
                self.result = None;
            def return_(self, result):
                self.result = result;

        return_ = Result();

        argument = "";
        argDict = {};
        count = -1;
        for i in args:
            count += 1;
            key = f"___{count}Object";
            argDict[key] = i;
            argument += f", {key}" if count > 0 else key;

        statement = f"{self.objs[name]}\n\nReturn({name}({argument}));";
        lib = globals(); lib.update({"Return": return_.return_}); lib.update(argDict);
        exec(statement, lib);
        return return_.result;

    '''Functions'''

    def export(self):
        with open(f"Engine_{self.version}", "wb+") as file:
            pickle.dump(self, file);

    def run(self):
        print(f"Welcome to botname version {self.version}");
        self.setBasicData();
        mem = self.c("Memory", self, None);
        test = TestClass(self, "Class");
        test.run();
        self.test("function");

    def test(self, admsg):
        print(f"Engine is working! Success: [{admsg}]");
        return True;
