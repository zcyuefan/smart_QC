#  Copyright 2008-2015 Nokia Solutions and Networks
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import difflib
import re
import time
from io import IOBase, StringIO
import token
from tokenize import generate_tokens, untokenize


def is_string(item):
    return isinstance(item, str)


def type_name(item):
    if isinstance(item, IOBase):
        return 'file'
    cls = item.__class__ if hasattr(item, '__class__') else type(item)
    named_types = {str: 'string', bool: 'boolean', int: 'integer',
                   type(None): 'None', dict: 'dictionary', type: 'class'}
    return named_types.get(cls, cls.__name__)


def as_dict(self, decoration=True):
    if decoration:
        variables = (self._decorate(name, self[name]) for name in self)
    else:
        variables = self.data
    return NormalizedDict(variables, ignore='_')


class _Misc():

    def evaluate(self, expression, modules=None, namespace=None):
        """Evaluates the given expression in Python and returns the results.

        ``expression`` is evaluated in Python as explained in `Evaluating
        expressions`.

        ``modules`` argument can be used to specify a comma separated
        list of Python modules to be imported and added to the evaluation
        namespace.

        ``namespace`` argument can be used to pass a custom evaluation
        namespace as a dictionary. Possible ``modules`` are added to this
        namespace. This is a new feature in Robot Framework 2.8.4.

        Variables used like ``${variable}`` are replaced in the expression
        before evaluation. Variables are also available in the evaluation
        namespace and can be accessed using special syntax ``$variable``.
        This is a new feature in Robot Framework 2.9 and it is explained more
        thoroughly in `Evaluating expressions`.

        Examples (expecting ``${result}`` is 3.14):
        | ${status} = | Evaluate | 0 < ${result} < 10 | # Would also work with string '3.14' |
        | ${status} = | Evaluate | 0 < $result < 10   | # Using variable itself, not string representation |
        | ${random} = | Evaluate | random.randint(0, sys.maxint) | modules=random, sys |
        | ${ns} =     | Create Dictionary | x=${4}    | y=${2}              |
        | ${result} = | Evaluate | x*10 + y           | namespace=${ns}     |
        =>
        | ${status} = True
        | ${random} = <random integer>
        | ${result} = 42
        """
        variables = self._variables.as_dict(decoration=False)
        expression = self._handle_variables_in_expression(expression, variables)
        namespace = self._create_evaluation_namespace(namespace, modules)
        variables = self._decorate_variables_for_evaluation(variables)
        try:
            if not is_string(expression):
                raise TypeError("Expression must be string, got %s."
                                % type_name(expression))
            if not expression:
                raise ValueError("Expression cannot be empty.")
            print("variables")
            return eval(expression, namespace, variables)
        except:
            raise RuntimeError("Evaluating expression '%s' failed"
                               % expression)

    def _handle_variables_in_expression(self, expression, variables):
        if not is_string(expression):
            return expression
        tokens = []
        variable_started = seen_variable = False
        generated = generate_tokens(StringIO(expression).readline)
        for toknum, tokval, _, _, _ in generated:
            if variable_started:
                if toknum == token.NAME:
                    if tokval not in variables:
                        raise Exception("Variable '%s' not found." %tokval)
                    tokval = 'SQC_VAR_' + tokval
                    seen_variable = True
                else:
                    tokens.append((token.ERRORTOKEN, '$'))
                variable_started = False
            if toknum == token.ERRORTOKEN and tokval == '$':
                variable_started = True
            else:
                tokens.append((toknum, tokval))
        if seen_variable:
            return untokenize(tokens).strip()
        return expression

    def _create_evaluation_namespace(self, namespace, modules):
        namespace = dict(namespace or {})
        modules = modules.replace(' ', '').split(',') if modules else []
        namespace.update((m, __import__(m)) for m in modules if m)
        return namespace

    def _decorate_variables_for_evaluation(self, variables):
        decorated = [('SQC_VAR_' + name, value)
                     for name, value in variables.items()]
        return NormalizedDict(decorated, ignore='_')

    @property
    def _variables(self):
        return self._namespace.variables

    @property
    def _namespace(self):
        return self._get_context().namespace

    @property
    def _context(self):
        return self._get_context()

    def _get_context(self, top=False):
        ctx = EXECUTION_CONTEXTS.current if not top else EXECUTION_CONTEXTS.top
        if ctx is None:
            raise RobotNotRunningError('Cannot access execution context')
        return ctx