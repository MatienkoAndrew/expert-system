import re
from enum import Enum
from .color import Color

OPERATORS = ['!', '+', '|', '^', '(', ')']
PRIORITY = {'!': 4, '+': 3, '|': 2, '^': 1}


class ImplyType(Enum):
	IMPLY = '=>'
	EQUAL = '<=>'


class RPNParser:
	@staticmethod
	def infix_to_postfix(expression: list):
		if len(expression) == 0:
			raise BaseException(f"{Color.WARNING}No rules for parsing{Color.END}")

		stack = []
		output = ''
		for ch in expression:
			if ch not in OPERATORS:
				output += ch
			elif ch == '(':
				stack.append(ch)
			elif ch == ')':
				while stack and stack[-1] != '(':
					output += stack.pop()
				stack.pop()
			else:
				while stack and stack[-1] != '(' and ch != '!' and PRIORITY[ch] <= PRIORITY[stack[-1]]:
					output += stack.pop()
				stack.append(ch)

		while stack:
			output += stack.pop()

		output = output.replace("!!", "")
		return output


class RPNRule(RPNParser):
	def __init__(self, rule: (str, list)):
		rule_split = re.split(r"=>|<=>", rule)
		self.type = (ImplyType.EQUAL if "<=>" in rule else ImplyType.IMPLY)

		left = list(rule_split[0].replace(" ", "").replace("\t", ""))
		right = list(rule_split[1].replace(" ", "").replace("\t", ""))

		self.left = self.infix_to_postfix(left)
		self.right = self.infix_to_postfix(right)

		# check if ! in conclusion exp: => !(A + B)
		if '+!' in self.right:
			raise BaseException(f'{Color.WARNING}Error at line : {rule} - Rule has bad format{Color.END}')

		# check if '|' in right exp: B | D <=> A
		if self.type == ImplyType.EQUAL and '|' in self.left:
			raise BaseException(f'{Color.WARNING}Error at line : {rule} - Rule has bad format{Color.END}')

		# check if ! in conclusion or left, exp: D + C <=> !(A + B) OR !(A + B) <=> D + C
		if self.type == ImplyType.EQUAL and ('+!' in self.right or '+!' in self.left):
			raise BaseException(f'{Color.WARNING}Error at line : {rule} - Rule has bad format{Color.END}')

	def __repr__(self):
		return f'<RPN Rule> left: {self.left}, right: {self.right}, type: {self.type}'
