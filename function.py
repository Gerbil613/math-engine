import math
from decimal import *
# TODO: 
# - add exponential annihilation (a^0=1)
# - translating from string to string might be trippy and only work for exponents since it's a 1 -> 2 length map
# multiplication Functions MUST have two children

getcontext().prec = 100

translator = {
    '^': '**',
    'ln': math.log,
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan
}

class Function:
    def __init__(self, content, *children):
        self.children = list(children)
        self.content = content
        self.contains_variable = self.check_contains_variable()

    def __str__(self):
        if len(self.children) == 2:
            return '('+str(self.children[0]) + self.content + str(self.children[1])+')'
        elif len(self.children) == 0:
            return str(self.content)
        elif len(self.children) == 1:
            return self.content + '(' + str(self.children[0]) + ')'

    def special_str(self):
        '''Function.special_str() -> str
        Outputs string representation of node, but every number is encased by Decimal(num)
        This is done to avoid floating-point error inherent to eval()'''
        if len(self.children) == 2:
            return '('+self.children[0].special_str() + self.content + self.children[1].special_str()+')'
        elif len(self.children) == 0:
            if self.content != 'x':
                return 'Decimal('+str(self.content)+')'
            else:
                return str(self.content)
        elif len(self.children) == 1:
            return self.content + '(' + self.children[0].special_str() + ')'

    def evaluate(self, x):
        string = self.special_str()
        for operation in translator:
            string = string.replace(operation, str(translator[operation]))
        
        return eval(string)

    def check_contains_variable(self):
        if self.content == 'x': return True
        elif type(self.content) == int or type(self.content) == float: return False
        out = False
        for function in self.children:
            out = out or function.contains_variable
        return out

    def simplify(self):
        for child in self.children:
            if len(child.children) >= 0: child.simplify()

        # multiplicative identity
        if self.content == '*':
            if self.children[1].content == 1:
                saved_children, saved_content = self.children[0].children, self.children[0].content
                self.children = saved_children
                self.content = saved_content
            
            elif self.children[0].content == 1:
                saved_children, saved_content = self.children[1].children, self.children[1].content
                self.children = saved_children
                self.content = saved_content

            # multiplicative annihilation
            elif self.children[0].content == 0 or self.children[1].content == 0:
                self.children = []
                self.content = 0
        
        # additive identity
        elif self.content == '+':
            if self.children[0].content == 0 or self.children[1].content == 0:
                target = self.children[0 if self.children[0].content != 0 else 1]
                self.children = target.children
                self.content = target.content

        elif self.content == '^':
            # exponential identity
            if self.children[0].content == 'x' and self.children[1].content == 1:
                self.content = 'x'
                self.children = []
            
            # exponential annihilation
            elif self.children[0].content == 'x' and self.children[1].content == 0:
                self.content = 1
                self.children = 0

        # simplify various functions
        elif self.content in translator and not self.contains_variable:
            if type(translator[self.content]) != str:
                val = translator[self.content](self.children[0].content)

            else:
                string = str(self)
                for i in range(len(string)):
                    if string[i:i+len(self.content)] == self.content:
                        string = string[:i] + translator[self.content] + string[i+len(self.content):]

                val = eval(string)

            if abs(Decimal(val) - Decimal(round(val, getcontext().prec))) <= 10**-(getcontext().prec):
                self.content = round(val, getcontext().prec)
                self.children = []

        self.check_contains_variable()

    def differentiate(self):
        if self.content == 'x': return Function(1)
        # derivative of constant is 0
        if not self.contains_variable:
            return Function(0)

        # additivity of differentiation
        if self.content == '+':
            sum = []
            for function in self.children: sum.append(function.differentiate())
            return Function('+', *sum)

        if self.content == '^' and self.contains_variable:
            # power rule
            if self.children[0].contains_variable and not self.children[1].contains_variable:
                n = Decimal(self.children[1].content)
                return Function('*', Function('*', Function(n), Function('^', self.children[0], Function(n-1))), self.children[0].differentiate())
            
            # exponent rule
            else:
                n = self.children[0].content
                return Function('*', self, Function('ln', Function(n)))

        # product rule
        if self.content == '*':
            a = self.children[0]
            b = self.children[1]
            return Function('+', Function('*', a.differentiate(), b), Function('*', a, b.differentiate()))

        # convert division into multiplication by reciprocal
        if self.content == '/':
            return Function('*', self.children[0], Function('^', self.children[1], Function(-1))).differentiate()

        if self.content == '-':
            return Function('+', self.children[0], Function('*', Function(-1), self.children[1])).differentiate()

        output = None
        # natural log
        if self.content == 'ln' and self.contains_variable:
            return Function('*', Function('^', self.children[0], Function(-1)), self.children[0].differentiate())

        # sine
        if self.content == 'sin' and self.contains_variable:
            return Function('*', Function('cos', self.children[0]), self.children[0].differentiate())

        # cosine
        if self.content == 'cos' and self.contains_variable:
            return Function('*', Function('*', Function(-1), Function('sin', self.children[0])), self.children[0].differentiate())

        # tangent
        if self.content == 'tan' and self.contains_variable:
            return Function('*', Function('^', Function('sec', Function('x')), Function(2)), self.children[0].differentiate())

x = Function('+', Function('^', Function('x'), Function(2)), Function('x')).differentiate()
x.simplify()
print(x)