class Rule:

    def __init__(self, id):
        self.id = id
        self.paths = []
        self.rule1 = None
        self.rule2 = None
        self.edges = []
        self.query = None
        self.graph = None
        self.target_types = set()

    def create_query(self):
        self.query = "ASK WHERE {\n"
        for edge in self.edges:
            source = edge[0]
            if source.startswith("X"):
                source = "?" + source
            else:
                source = "<" + source + ">"
            target = edge[1]
            if target.startswith("X"):
                target = "?" + target
            else:
                target = "<" + target + ">"

            self.query += "{ " + source + " ?p " + target + ". } UNION {" + target + " ?p " + source + ". }\n"
        self.query += "}"

        # print("QUERY",self.query)

    def create_edges(self):
        for path in self.paths:
            for i in range(0, len(path) - 1):
                self.edges.append([path[i], path[i + 1]])
