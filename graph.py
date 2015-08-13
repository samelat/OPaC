import re

class OPaCRegex:
    def __init__(self, entries):
        self.entries = entries
        self.tree = None


    def fragment(self, groups):
        result = []
        sizes = []

        last_group = groups.pop(0)
        while groups:
            group = groups.pop(0)

            intersection_size = 0
            for size in range(1, min(len(last_group), len(group)) + 1):
                print('[compare] size {0}'.format(size))
                if last_group[-1*size:] == group[:size]:
                    intersection_size = size
                    break

            if intersection_size:
                print('[intersecting] {0} && {1}'.format(last_group, group))
                result.append(last_group[:-1*intersection_size])
                result.append(last_group[ -1*intersection_size:])
                result.append(group[:intersection_size])

                last_group = group[intersection_size:]

            else:
                result.append(last_group)
                last_group = group

        result.append(last_group)

        return result


    def compress(self, groups):
        result = []
        sizes = []

        group_size = 1
        last_group = groups.pop(0)
        while groups:
            group = groups.pop(0)
            if last_group == group:
                group_size += 1
            else:
                result.append(last_group)
                sizes.append(group_size)
                last_group = group
                group_size = 1

        sizes.append(group_size)
        result.append(last_group)

        return result, sizes


    def digest(self):
        
        for entry in self.entries:
            print('*'*64)
            words = re.findall('(\d+|[^\W_]+|[\W_])', entry)

            print(words)

            groups = []
            group = []
            for word in words:
                if re.match('\d', word[0]):
                    token = '\d'

                elif re.match('[^\W_]', word[0]):
                    token = '[^\W_]'

                else:
                    token = '\\' + word[0]

                if token in group:
                    groups.append(tuple(group))
                    group = []
                
                group.append(token)

            groups.append(tuple(group))
            print(groups)

            groups = self.fragment(groups)

            print(groups)

            groups = self.compress(groups)

            print(groups)

                