class FakeResponse:
    def __init__(self, data: list[dict]):
        self.data = data


class FakeQueryBuilder:
    def __init__(self, data: list[dict]):
        self._data = data
        self.calls: list[tuple] = []

    def select(self, *args):
        self.calls.append(("select", args))
        return self

    def eq(self, *args):
        self.calls.append(("eq", args))
        return self

    def gte(self, *args):
        self.calls.append(("gte", args))
        return self

    def lte(self, *args):
        self.calls.append(("lte", args))
        return self

    def like(self, *args):
        self.calls.append(("like", args))
        return self

    def order(self, *args):
        self.calls.append(("order", args))
        return self

    def limit(self, *args):
        self.calls.append(("limit", args))
        return self

    def execute(self):
        return FakeResponse(self._data)


class FakeSupabaseClient:
    def __init__(self, data: list[dict]):
        self._data = data
        self.last_query_builder: FakeQueryBuilder | None = None

    def table(self, name: str) -> FakeQueryBuilder:
        self.last_query_builder = FakeQueryBuilder(self._data)
        self.table_name = name
        return self.last_query_builder
