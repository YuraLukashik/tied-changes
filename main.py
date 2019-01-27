from git import Repo
from git import Diff

repo = Repo('../../overlai/api')

commits = list(repo.iter_commits())
commits.reverse()

EMPTY_TREE_SHA = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"

class Graph:

    def __init__(self):
        self.graph = {}
        self.indexes = {}

    def inc(self, v1, v2):
        i1 = self.__get_index(v1)
        i2 = self.__get_index(v2)
        if i1 == i2:
            return
        if (i1, i2) in self.graph:
            self.graph[(i1, i2)] += 1
            self.graph[(i2, i1)] += 1
        else:
            self.graph[(i1, i2)] = 1
            self.graph[(i2, i1)] = 1

    def rename(self, v1, v2):
        i1 = self.__get_index(v1)
        self.indexes[v2] = i1
        self.indexes.pop(v1)

    def __get_index(self, v):
        if not(v in self.indexes):
            self.indexes[v] = len(self.indexes) + 1
        return self.indexes[v]

    def __str__(self):
        return str(self.graph)+"\n"+str(self.indexes)

    def sort(self):
        l = [(t, self.graph[t]) for t in self.graph.keys()]
        l.sort(key=lambda x: x[1], reverse=True)
        names = {}
        for name in self.indexes.keys():
            names[self.indexes[name]] = name
        res = []
        for pair in l:
            try:
                res.append(names[pair[0][0]]+" "+names[pair[0][1]]+" "+str(pair[1]))
            except KeyError:
                res.append('error')
        print(res[0::20])

graph = Graph()

i = 0
for key, commit in enumerate(commits):
    if len(commit.parents) == 0:
        diff = commit.diff(EMPTY_TREE_SHA)
    else:
        diff = commit.diff(commit.parents[0])
    diff = list(diff)
    if key+1 < len(commits):
        diff += list(commit.diff(commits[key+1]))
    if key+2 < len(commits):
        diff += list(commits[key+1].diff(commits[key+2]))
    if key+3 < len(commits):
        diff += list(commits[key+2].diff(commits[key+3]))
    for file1 in diff:
        for file2 in diff:
            if file1.renamed_file:
                graph.rename(file1.a_path, file1.b_path)
            if file2.renamed_file:
                graph.rename(file2.a_path, file2.b_path)
            graph.inc(file1.b_path, file2.b_path)
    i += 1
    print(i)

graph.sort()

