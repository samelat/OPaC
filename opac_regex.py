import re

''' ##############################################################

    ##############################################################
'''
class OPaCRegex:

    def __init__(self):
        self.samples = []

    def digest(self, samples):

        templates = {}
        for sample in samples:
            print(sample)
            sample = Sample(sample)
            template = tuple(sample.template)

            if template not in templates:
                templates[template] = []
            templates[template].append(sample)

        print(templates)

        # Select Best Template and Its samples
        sorted_templates = [(len(samples), template) for template, samples in templates.items()]
        sorted_templates.sort(reverse=True)
        best_template = sorted_templates[0][1]
        self.samples = templates[best_template]

        template = Template(best_template, self.samples)

        template.sharpen()
        #return template.compile()


''' ##############################################################

    ##############################################################
'''
class Template:
    def __init__(self, template, samples):
        self.samples = samples
        self.template = template

    def sharpen(self):

        #heights = [sample.heights for sample in self.samples]
        heights_union = [set([height]) for height in self.samples[0].heights]

        for height_index in range(0, len(heights_union)):
            heights_union[height_index].update([sample.heights[height_index] for sample in self.samples[1:]])



        #grouped_tokens_union = [set(token) for token in self.samples[0].group_tokens()]
        samples_grouped_tokens = [sample.group_tokens() for sample in self.samples]

        for grouped_tokens in samples_group_tokens:
            for tokens_group in grouped_tokens:

        print(all_grouped_tokens[0])

        grouped_tokens_union = []
        for group_index in range(0, len(self.template)):
            group_union = []
            for token_index in range(0, len(self.template[group_index])):
                for grouped_tokens in all_grouped_tokens
                tokens_union = set([grouped_tokens[group_index][token_index] ])
                group_union.append(tokens_union)
            grouped_tokens_union.append(group_union)

        print(grouped_tokens_union)

        return

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

        return (sharped_template, sharped_heights)


    def compile(self, template, heights):
        print('[compile] heights: {0}'.format(heights))
        print('[compile] template: {0}'.format(template))
        for entry in self.entries.values():
            print('[compile] entry: {0}'.format(entry['grouped_tokens']))

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
                    regex += '{{{0}}}'.format(height)

            elif len(group_heights) == 2:
                regex += '({0})'.format(group_regex)
                group_range = list(group_heights)
                group_range.sort()
                regex += '{{{0},{1}}}'.format(*group_range)

            else:
                regex += '({0})'.format(group_regex)
                regex += '+'

        return regex


''' ##############################################################

    ##############################################################
'''
class Sample:

    def __init__(self, sample):
        self.tokens = re.findall('([^\W_]+|[\W_])', sample)
        template = self.digest_tokens()
        template = self.fragment(template)
        self.template, self.heights = self.compress(template)

    def __hash__(self):
        return hash(tuple(self.template))

    def group_tokens(self):
        weights = [len(group) for group in self.template]

        result = []
        last_index = 0
        for height, weight in zip(self.heights, weights):
            group = []
            for index in range(last_index, last_index + height*weight, weight):
                row.append(self.tokens[index:index+weight])

                last_index = index + weight

            result.append(group)
        return result

    def digest_tokens(self):
        regexes = []
        group = []
        for token in self.tokens:
            if re.match('^\d+$', token):
                regex_token = '\d'

            elif re.match('[^\W_]+', token[0]):
                regex_token = '[^\W_]'

            else:
                regex_token = '\\' + token[0]

            if regex_token in group:
                regexes.append(tuple(group))
                group = []
            
            group.append(regex_token)

        regexes.append(tuple(group))
        return regexes


    def fragment(self, template):
        fragmented_template = []
        sizes = []

        last_group = template.pop(0)
        while template:
            group = template.pop(0)

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
                fragmented_template.extend(fragments)

            else:
                fragmented_template.append(last_group)
                last_group = group

        fragmented_template.append(last_group)
        return fragmented_template


    def compress(self, template):
        result = []
        sizes = []

        group_size = 1
        last_group = template.pop(0)
        while template:
            group = template.pop(0)
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

