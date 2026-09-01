class FakeChatModel:
    """Fake stand-in for a langchain ChatOpenAI (or any chat model) whose
    with_structured_output(...) is used. Captures the schema it was asked
    to structure output as, and always returns a fixed instance of it."""

    def __init__(self, structured_output: object):
        self.structured_output = structured_output
        self.captured_schema = None

    def with_structured_output(self, schema):
        self.captured_schema = schema

        def _invoke(prompt_value):
            return self.structured_output

        return _invoke
