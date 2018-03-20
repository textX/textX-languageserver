__author__ = "Nemanja Starčev"
__copyright__ = "textX-tools"
__license__ = "MIT"


class ColoringVSCode(object):

    def __init__(self, config):
        self.config = config
        self.textxRulesInProgram = {}
        self.keywords = []
        self.operations = []
        self.rule_keyword_relation = []
        self.rule_operation_relation = []
        self.special_characters = ['+', '*', '?', '|', '.', '(',
                                   ')', '$', '[', ']', '\\', '^']

        self.additional_characters = ['<', '>', '=', '+', '-', '*', '/',
                                      '|', '&', '(', ')', '~', '!', '@',
                                      '#', '$', '[', ']', '{', '}', ',',
                                      '.', ';', ':', '?', '%', '\\', '^']

        self.default_keyword_type = None
        self.default_operation_type = None
        self.line_comment = None
        self.block_comment_start = None
        self.block_comment_end = None
        self.rules_keyword_type_relation = {}
        self.rules_operation_type_relation = {}
        self.matches_word_type_relation = {}
        self.regular_expressions = {}

        self.keyword_type_relation = {}
        self.operation_type_relation = {}
        self.regular_expression_type_relation = {}
        self.type_keyword_relation = {}
        self.type_operation_relation = {}
        self.type_regular_expression_relation = {}

        self.coloring_model = {}

    def get_coloring_model(self):
        self._interpret_grammar(self.config.grammar_model)
        self._interpret_program(self.config.coloring_model)

        self._prepare_data()
        return self.coloring_model

    def _interpret_program(self, model):
        if model.configuration is not None:
            self._interpret_configuration(model.configuration)
        for element in model.array:
            if element.rules is not None:
                self._intepret_rules(element.rules)
            if element.matches is not None:
                self._interpret_matches(element.matches)
            if element.regular_expressions is not None:
                self._interpret_regular_expressions(element.
                                                    regular_expressions)

    def _interpret_configuration(self, configuration):
        for command in configuration.configuration_commands:
            if command.default is not None:
                self._interpret_default(command.default)
            if command.lang_comment is not None:
                self._interpret_comment(command.lang_comment)

    def _interpret_default(self, default):
        for option in default.default_options:
            if option.default_keyword_option is not None:
                self.default_keyword_type = option.default_keyword_option.type
            if option.default_operation is not None:
                self.default_operation_type = option.default_operation.type

    def _interpret_comment(self, comment):
        for option in comment.comment_options:
            if option.line is not None:
                self.line_comment = \
                    self._escape_spec_chars(option.line.id)
            if option.block is not None:
                self.block_comment_start = \
                    self._escape_spec_chars(option.block.start)
                self.block_comment_end = \
                    self._escape_spec_chars(option.block.end)

    def _intepret_rules(self, rules):
        for option in rules.rule_options:
            if option.rule_keyword is not None:
                for list in option.rule_keyword.rule_lists:
                    for element in list.elements:
                        self.rules_keyword_type_relation[element] = list.type
            if option.rule_operation is not None:
                for list in option.rule_operation.rule_lists:
                    for element in list.elements:
                        self.rules_operation_type_relation[element] = list.type

    def _interpret_matches(self, matches):
        for list in matches.match_list:
            for word in list.words:
                escaped = self._escape_spec_chars(word)
                self.matches_word_type_relation[escaped] = list.type

    def _interpret_regular_expressions(self, regular_expressions):
        for list in regular_expressions.regular_expression_list:
            for expression in list.expression:
                self.regular_expressions[expression] = list.type

    def _interpret_grammar(self, model):
        for rule in model.rules:
            self._interpret_sequences(rule.body.sequences, rule.name)

    def _interpret_sequences(self, sequences, rule_name):
        for sequence in sequences:
            for expression in sequence.repeatable_expr:
                if expression.expr.simple_match is not None and \
                   expression.expr.simple_match.str_match is not None:

                    match = expression.expr.simple_match.str_match.match
                    self._append_word(rule_name, match)

                assignment = expression.expr.assignment
                if assignment is not None and \
                        assignment.rhs is not None:
                    rhs = assignment.rhs
                    if rhs.simple is not None and \
                            rhs.simple.str_match is not None:

                        self._append_word(rule_name,
                                          rhs.simple.str_match.match)

                    if rhs.modifiers is not None and \
                            rhs.modifiers.str_match is not None:
                        self._append_word(rule_name,
                                          rhs.modifiers.str_match.match)

                oper = expression.operator
                if oper is not None and \
                        oper.modifiers is not None and \
                        oper.modifiers.str_match is not None:
                    self._append_word(rule_name,
                                      oper.modifiers.str_match.match)

                if expression.expr.bracketed_choice is not None:
                    choice = expression.expr.bracketed_choice.choice
                    self._interpret_sequences(choice.sequences, rule_name)

    def _append_word(self, rule_name, word):
        if self._word_from_add_chars(word):
            word = self._escape_spec_chars(word)
            if word not in self.operations:
                self.operations.append(word)
            operation = {'rule': rule_name, 'operation': word}
            self.rule_operation_relation.append(operation)
        else:
            word = self._escape_spec_chars(word)
            if word not in self.keywords:
                self.keywords.append(word)
            keyword = {'rule': rule_name, 'keyword': word}
            self.rule_keyword_relation.append(keyword)

    def _word_from_add_chars(self, word):
        for character in word:
            if character not in self.additional_characters:
                return False
        return True

    def _escape_spec_chars(self, word):
        retVal = ""
        for _, character in enumerate(word):
            if character not in self.special_characters:
                retVal += character
            else:
                retVal += '\\\\'
                retVal += character
        return retVal

    def _prepare_data(self):
        self._prepare_relation_keywords()
        self._prepare_relation_operations()
        self._prepare_types()
        self._prepare_coloring_json()

    def _prepare_relation_keywords(self):
        for item in self.matches_word_type_relation:
            if item not in self.keywords and \
                    self._word_from_add_chars(item) is False:

                self.keywords.append(item)
        for item in self.keywords:
            self.type = self._get_type_from_keywords(item)
            if item not in self.keyword_type_relation and \
                    self.type is not None:
                self.keyword_type_relation[item] = self.type
                continue
            self.type = self._get_type_from_rules_keyword(item)
            if self.type is not None:
                self.keyword_type_relation[item] = self.type
                continue
            if self.default_keyword_type is not None:
                self.keyword_type_relation[item] = self.default_keyword_type

    def _prepare_relation_operations(self):
        for item in self.matches_word_type_relation:
            if item not in self.operations and self._word_from_add_chars(item):
                self.operations.append(item)
        for item in self.operations:
            self.type = self._get_type_from_keywords(item)
            if item not in self.operation_type_relation and \
                    self.type is not None:
                self.operation_type_relation[item] = self.type
                continue
            self.type = self._get_type_from_rules_operation(item)
            if self.type is not None:
                self.operation_type_relation[item] = self.type
                continue
            if self.default_operation_type is not None:
                self.operation_type_relation[item] = \
                    self.default_operation_type

    def _get_type_from_keywords(self, word):
        self.type = None
        for item in self.matches_word_type_relation:
            if item == word:
                self.type = self.matches_word_type_relation.get(item)
        if self.type is not None:
            return self.type
        for item in self.keyword_type_relation:
            if item == word:
                self.type = self.keyword_type_relation.get(item)
        return self.type

    def _get_type_from_rules_keyword(self, word):
        self.type = None
        for item in self.rule_keyword_relation:
            if item['keyword'] == word:
                for relation in self.rules_keyword_type_relation:
                    if relation == item['rule']:
                        self.type = self.rules_keyword_type_relation[relation]
        return self.type

    def _get_type_from_rules_operation(self, word):
        self.type = None
        for item in self.rule_operation_relation:
            if item['operation'] == word:
                for rel in self.rules_operation_type_relation:
                    if rel == item['rule']:
                        self.type = self.rules_operation_type_relation[rel]
        return self.type

    def _prepare_types(self):
        for item in self.keyword_type_relation:
            kw_type_rel = self.keyword_type_relation[item]
            if kw_type_rel not in self.type_keyword_relation:
                self.type_keyword_relation[kw_type_rel] = []
            if item is not "'" and item is not '"' and \
                    self._word_from_add_chars(item) is False:
                self.type_keyword_relation[kw_type_rel].append(item)
            elif item is not "'" and item is not '"':
                self.type_keyword_relation[kw_type_rel].append(item)
        for item in self.operation_type_relation:
            op_type_rel = self.operation_type_relation[item]
            if op_type_rel not in self.type_operation_relation:
                self.type_operation_relation[op_type_rel] = []
            self.type_operation_relation[op_type_rel].append(item)
        for item in self.regular_expressions:
            reg_ex = self.regular_expressions[item]
            if reg_ex not in self.type_regular_expression_relation:
                self.type_regular_expression_relation[reg_ex] = []
            self.type_regular_expression_relation[reg_ex].append(item)
            self.type_regular_expression_relation[reg_ex].append(item)

    def _prepare_coloring_json(self):
        kw_rel = self._get_name_match_relation(self.type_keyword_relation,
                                               True)
        op_rel = self._get_name_match_relation(self.type_operation_relation)

        reg_ex = self.type_regular_expression_relation
        reg_ex_rel = self._get_name_match_relation(reg_ex)

        self.coloring_model = {
            'name': self.config.language_name,
            'extensions': self.config.lang_ext_double_quoted,
            'comment': {
                'line': self.line_comment,
                'block_start': self.block_comment_start,
                'block_end': self.block_comment_end
            },
            'keywords': kw_rel,
            'operations': op_rel,
            'regular_expressions': reg_ex_rel
        }

    def _get_name_match_relation(self, map, word_boundary=False):
        keywords = []
        deleted = True
        while deleted is True:
            deleted = False
            for item, words in map.items():
                element = ""
                j = 0
                insert = False
                while j < len(words):
                    if j >= len(words):
                        break
                    independent = self._is_word_indep(words[j], item, map)
                    if independent is False:
                        j = j + 1
                        continue
                    string = ""
                    if word_boundary:
                        string += "\\\\b"
                    string += words[j]
                    if word_boundary:
                        string += "\\\\b"
                    element += string
                    if j != len(words)-1:
                        element += '|'
                    words.remove(words[j])
                    deleted = True
                    insert = True
                keyword = {
                    'name': item,
                    'match': element
                }
                if insert:
                    keywords.append(keyword)
        return keywords

    def _is_word_indep(self, word, type, map):
        for key, value in map.items():
            for item in value:
                if key != type and word in item:
                    return False
        return True
