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

        template = []
        for group_index in range(0, len(best_template)):
            group = RegexGroup(best_template[group_index], group_index)
            for sample in self.samples:
                group.use_sample(sample)
            template.append(group)

        regex = ''
        #for group in template:
        #    group.sharpen()
        #    regex += group.compile()
        print(template[0].heights)
        print(template[0].cardinalities)
        print(template[0].prefix)
        print(template[0].postfix)

        print(best_template)

        return regex


''' ##############################################################

    ##############################################################
'''
class RegexGroup:
    def __init__(self, template, index):
        self.index = index
        self.template = template
        self.heights = set()
        self.cardinalities = []
        for token_regex in self.template:
            self.cardinalities.append(set())
        self.prefix = None
        self.postfix = None


    def use_sample(self, sample):

        group_samples = sample.group(self.index)
        self.heights.add(sample.heights[self.index])

        group_sets = []
        for token_index in range(0, len(self.template)):
            token_set = set()
            for group_sample in group_samples:
                self.cardinalities[token_index].add(len(group_sample[token_index]))
                token_set.add(group_sample[token_index])
            group_sets.append(token_set)

        if not self.prefix:
            self.prefix = [{token} for token in group_samples[0]]
        else:
            for group_index in range(0, len(self.postfix)):
                self.prefix[group_index] = self.prefix[group_index].intersection(group_samples[0][group_index])

        if not self.postfix:
            self.postfix = [{token} for token in group_samples[-1]]
        else:
            for group_index in range(0, len(self.postfix)):
                self.postfix[group_index] = self.postfix[group_index].intersection(group_samples[-1][group_index])


    def sharpen(self):

        sharped_heights = []
        sharped_template = []
        for group_index in range(0, len(self.template)):
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
        self.tokens = re.findall('([^\W_]+|[\W_]+)', sample)
        template = self.digest_tokens()
        template = self.fragment(template)
        self.template, self.heights = self.compress(template)
        self.weights = [len(group) for group in self.template]

    def __hash__(self):
        return hash(tuple(self.template))

    def group(self, group_index):
        samples = []

        weight = self.weights[group_index]
        height = self.heights[group_index]
        last_index = sum([self.weights[index]*self.heights[index] for index in range(0, group_index)])
        for token_index in range(last_index, last_index + height*weight, weight):
            samples.append(self.tokens[token_index:token_index+weight])

            last_token_index = token_index + weight

        return samples

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

