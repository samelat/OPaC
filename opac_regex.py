import re



class OPaCRegex:

    def __init__(self, rows):
        self.rows = rows


    def words_to_regexes(self, words):
        pass


    def digest(self):

        tokens_stacks = []
        for row in self.rows:
            tokens = re.findall('(\d+|[^\W_]+|[\W_])', row)
            tokens_stacks.append(tokens)

        regex_stacks = [[]]
        while tokens_stacks:
            tokens = set()
            new_tokens_stacks = []
            for tokens_stack in tokens_stacks:
                tokens.add(tokens_stack.pop(0))
                if tokens_stack:
                    new_tokens_stacks.append(tokens_stack)
            tokens_stacks = new_tokens_stacks

            print(tokens)

            if len(tokens) == 1:

