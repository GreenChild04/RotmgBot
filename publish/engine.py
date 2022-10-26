import pickle;
import base64;
from dill.source import getsource;
import sys;

class Engine:
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

    '''Function Redirects'''

    def run(self): return self.r("run");
    def export(self): return self.r("export");
    def test(self, a): return self.r("test", a);


'''Classes'''
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
