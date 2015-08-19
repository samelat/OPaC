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
            sample = Sample(sample)
            template = tuple(sample.template)

            if template not in templates:
                templates[template] = []
            templates[template].append(sample)

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
        for group in template:
            group.sharpen()
            regex += group.compile()

        return regex


''' ##############################################################

    ##############################################################
'''
class RegexGroup:
    def __init__(self, template, index):
        self.index = index
        self.template = [template]
        self.heights = set()
        self.cardinalities = []
        self.cardinalities.append([set() for token_regex in self.template[0]])
        self.fixes = [set(), set()] # Prefix and Postfix


    def use_sample(self, sample):

        group_samples = sample.group(self.index)
        self.heights.add(sample.heights[self.index])

        group_sets = []
        for token_index in range(0, len(self.template[0])):
            token_set = set()
            for group_sample in group_samples:
                self.cardinalities[0][token_index].add(len(group_sample[token_index]))
                token_set.add(group_sample[token_index])
            group_sets.append(token_set)

        self.fixes[0].add(tuple(group_samples[0]))
        self.fixes[1].add(tuple(group_samples[-1]))


    def sharpen(self):
        
        heights = []
        template = []
        cardinalities = []
        for fix_tokens in self.fixes:
            fix = [set(tokens) for tokens in zip(*fix_tokens)]
            group_cardinalities = []

            self.heights = list(filter(bool, self.heights))
            if not len(self.heights):
                break

            for index in range(0, len(self.template[0])):
                cardinality = set()
                if self.template[0][index] in ['[^\\W_]', '\\d']:
                    if len(fix[index]) > 1:
                        fix[index] = self.template[0][index]
                        cardinality = self.cardinalities[0][index]
                    else:
                        fix[index] = fix[index].pop()
                        cardinality = {1}
                        self.cardinalities[0][index] -= {len(fix[index])}
                else:
                    fix[index] = self.template[0][index]
                    cardinality = self.cardinalities[0][index]
                group_cardinalities.append(cardinality)

            if tuple(fix) != self.template[0]:
                self.heights = [height-1 for height in self.heights]
                heights.append([1])
                cardinalities.append(group_cardinalities)
                template.append(tuple(fix))

        heights.insert(1, self.heights)
        template.insert(1, self.template[0])
        cardinalities.insert(1, self.cardinalities[0])
        self.heights = heights
        self.template = template
        self.cardinalities = cardinalities


    def cardinality_token(self, cardinality):
        cardinality = list(cardinality)

        if len(cardinality) > 2:
            return '+'

        elif len(cardinality) == 2:
            cardinality.sort()
            return '{{{0},{1}}}'.format(*cardinality)

        elif (len(cardinality) == 1) and (cardinality[0] > 1):
            return '{{{0}}}'.format(*cardinality)

        return ''


    def compile(self):

        regex = ''
        for group_index in range(0, len(self.template)):
            if not self.heights[group_index]:
                continue

            subregex = ''
            for token_index in range(0, len(self.template[group_index])):
                subregex += self.template[group_index][token_index]
                subregex += self.cardinality_token(self.cardinalities[group_index][token_index])

            group_cardinality = self.cardinality_token(self.heights[group_index])
            if group_cardinality:
                subregex = '({0}){1}'.format(subregex, group_cardinality)

            regex += subregex

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

