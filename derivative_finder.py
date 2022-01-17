import math
from decimal import *
# TODO: 
# - deal with irrationals/too long decimals
# - add additive identity
# - add exponential identity (a^1=a)
# - add exponential annihilation (a^0=1)
# multiplication nodes MUST have two children

getcontext().prec = 10

def is_num(num):
    is_number = True
    try: Decimal(num)
    except Exception: return False
    return True

class Node:
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

    def check_contains_variable(self):
        if self.content == 'x': return True
        elif type(self.content) == int or type(self.content) == float: return False
        out = False
        for node in self.children:
            out = out or node.contains_variable
        return out

    def check_evaluatable(self):
        # first thing is for functions like sin, ln, second is just if there's an x it's a no-go
        if (self.content not in ['+','-','*','/','^'] and not is_num(self.content)) or self.contains_variable:
            return False
        
        out = True
        for child in self.children: out = out and child.check_evaluatable()
        return out

    def simplify(self):
        for i in range(len(self.children)):
            if self.children[i].check_evaluatable():
                string = str(self.children[i])
                for j in range(len(string)):
                    if string[j] == '^': string = string[:j] + '**' + string[j+1:]
                
                self.children[i] = Node(eval(string))

            elif self.children[i].content != 'x':
                self.children[i].simplify()

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

        self.check_contains_variable()

    def differentiate(self):
        if self.content == 'x': return Node(1)
        # derivative of constant is 0
        if not self.contains_variable:
            return Node(0)

        # additivity of differentiation
        if self.content == '+':
            sum = []
            for node in self.children: sum.append(node.differentiate())
            return Node('+', *sum)

        if self.content == '^' and self.contains_variable:
            # power rule
            if self.children[0].contains_variable and not self.children[1].contains_variable:
                n = Decimal(self.children[1].content)
                return Node('*', Node('*',Node(n), Node('^', self.children[0], Node(n-1))), self.children[0].differentiate())
            
            # exponent rule
            else:
                n = self.children[0].content
                return Node('*', self, Node('ln', Node(n)))

        # product rule
        if self.content == '*':
            a = self.children[0]
            b = self.children[1]
            return Node('+', Node('*', a.differentiate(), b), Node('*', a, b.differentiate()))

        # convert division into multiplication by reciprocal
        if self.content == '/':
            return Node('*', self.children[0], Node('^', self.children[1], Node(-1))).differentiate()

        # natural log
        if self.content == 'ln' and self.contains_variable:
            return Node('*', Node('^', self.children[0], Node(-1)), self.children[0].differentiate())

        # sine
        if self.content == 'sin' and self.contains_variable:
            return Node('*', Node('cos', self.children[0]), self.children[0].differentiate())

        if self.content == 'cos' and self.contains_variable:
            return Node('*', Node('*', Node(-1), Node('sin', self.children[0])), self.children[0].differentiate())

func = Node('+', Node('x'), Node(0))
print(func)
print(func)