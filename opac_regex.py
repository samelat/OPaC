import re

class OPaCRegex:
    def __init__(self, entries):
        self.entries = {}
        for entry in entries:
            self.entries[entry] = {}

    def fragment(self, groups):
        result = []
        sizes = []

        last_group = groups.pop(0)
        while groups:
            group = groups.pop(0)

            intersection_size = 0
            for size in range(1, min(len(last_group), len(group)) + 1):
                if last_group[-1*size:] == group[:size]:
                    intersection_size = size
                    break

            if intersection_size:
                fragments = [last_group[:-1*intersection_size],
                             last_group[ -1*intersection_size:],
                             group[:intersection_size],
                             group[intersection_size:]]
                fragments = [group for group in fragments if group]

                last_group = fragments.pop()
                result.extend(fragments)

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


    def group_tokens(self, sizes, tokens):
        result = []
        last_index = 0
        for height, weight in sizes:
            row = []
            for index in range(last_index, last_index + height*weight, weight):
                entry = ''.join(tokens[index:index+weight])
                row.append(entry)

                last_index = index + weight

            result.append(row)

        return result


    def template(self, tokens):

        group = []
        template = []
        for token in tokens:
            if re.match('\d', token[0]):
                regex_token = '\d'

            elif re.match('[^\W_]', token[0]):
                regex_token = '[^\W_]'

            else:
                regex_token = '\\' + token[0]

            if regex_token in group:
                template.append(tuple(group))
                group = []
            
            group.append(regex_token)

        template.append(tuple(group))
        return template


    def sharpen(self, template):
        match_entries = [entry for entry in self.entries.values() if entry['template'] == template]

        groups_heights = [entry['heights'] for entry in match_entries]
        groups_heights_union = [set([height]) for height in groups_heights.pop()]
        for height_index in range(0, len(groups_heights_union)):
            groups_heights_union[height_index].update([heights[height_index] for heights in groups_heights])

        grouped_tokens = [entry['grouped_tokens'] for entry in match_entries]
        grouped_tokens_union = [set(tokens_group) for tokens_group in grouped_tokens.pop()]
        
        for group_index in range(0, len(grouped_tokens_union)):
            for tokens_group in grouped_tokens:
                grouped_tokens_union[group_index] = grouped_tokens_union[group_index].intersection(tokens_group[group_index])

        sharped_heights = []
        sharped_template = []
        for group_index in range(0, len(grouped_tokens_union)):
            if grouped_tokens_union[group_index]:
                tokens_group = [token for token in grouped_tokens[0][group_index]
                                      if  token in grouped_tokens_union[group_index]]
                for token in tokens_group:
                    sharped_heights.append({1})
                    sharped_template.append((token,))
                    sharped_template.append(template[group_index])

                    updated_heights = set([height-1 for height in groups_heights_union[group_index]])
                    sharped_heights.append(updated_heights)

            else:
                sharped_heights.append(groups_heights_union[group_index])
                sharped_template.append(template[group_index])

        print(sharped_template)
        print(sharped_heights)

        return (sharped_template, sharped_heights)


    def compile(self, template, heights):

        regex = ''
        for group_index in range(0, len(template)):
            group = template[group_index]
            group_regex = ''
            for token in group:
                group_regex += token
                if token in ['[^\\W_]', '\\d']:
                    group_regex += '+'

            group_heights = heights[group_index]

            if len(group_heights) == 1:
                height = group_heights.pop()
                if not height:
                    continue

                regex += group_regex
                if height > 1:
                    regex += '{{{0}}}'.format(*group_heights)

            elif len(group_heights) == 2:
                regex += '({0})'.format(group_regex)
                regex += '{{{0},{1}}}'.format(*group_heights)

            else:
                regex += '({0})'.format(group_regex)
                regex += '+'

        return regex


    def digest(self):

        templates = {}
        for entry in self.entries:
            tokens = re.findall('(\d+|[^\W_]+|[\W_])', entry)

            template = self.template(tokens)
            template = self.fragment(template)
            template, heights = self.compress(template)

            # El template tendria que ser como el Identificador del proceso
            # que se esta haciendo, entonces en group_tokens, solo se deberia
            # especificar los tokens y el template (las unicas 2 cosas que se
            # necesitan :) ).
            weights = [len(group) for group in template]
            grouped_tokens = self.group_tokens(list(zip(heights, weights)), tokens)
            self.entries[entry]['grouped_tokens'] = grouped_tokens
            self.entries[entry]['heights'] = heights

            template = tuple(template)
            self.entries[entry]['template'] = template

            if template not in templates:
                templates[template] = 0
            templates[template] += 1

        sorted_templates = [(value, template) for template,value in templates.items()]
        sorted_templates.sort(reverse=True)
        best_template = sorted_templates[0][1]

        sharped_template, sharped_heights = self.sharpen(best_template)

        return self.compile(sharped_template, sharped_heights)