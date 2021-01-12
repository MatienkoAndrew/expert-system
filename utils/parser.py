from .rpn_parser import RPNRule
from .color import Color
import re


class Parser:
	def __init__(self, data: list):
		self.data = data
		self.rules = []
		self.facts = []
		self.queries = []
		self.rpn_rules = []
		self.atoms = []

		self.ft_parser()
		self.set_rules()

	def set_rules(self):
		for rule in self.rules:
			self.rpn_rules.append(RPNRule(rule))

	@staticmethod
	def check_atoms(atoms: list, facts_or_rules: str):
		fact_or_rule = list(filter(None, re.split(r"\?|=|\s", facts_or_rules)))
		fact_or_rule = re.findall(r'.', fact_or_rule[0]) if len(fact_or_rule) != 0 else []
		for elem in fact_or_rule:
			if elem not in atoms:
				return False
		return True

	@staticmethod
	def find_all_atoms(rules: list):
		atom = []
		for rule in rules:
			atom.append(list(filter(None, re.findall(r"[A-Z]*", rule))))
		atom = sorted(list(set([x for array in atom for x in array])))
		return atom

	@staticmethod
	def ft_check_parentheses(line: str):
		return line.count("(") == line.count(")")

	def ft_parser(self):
		# if '\n' not in self.data[-1]:
		# 	print("ERROR: ")
		# 	exit(1)
		lines = [x.strip() for x in self.data]
		lines = list(filter(None, lines))

		pattern_rules = re.compile(
			r"(^((\()*(\s)*(!){0,2})*(\s)*[A-Z](\s)*(\))*((\s*[+^|]\s*((\()*(\s)*(!){0,2})*(\s)*[A-Z]"
			r"(\s)*(\))*)*)?\s*(=>|<=>)\s*((\()*(\s)*(!){0,2})*[A-Z](\s)*(\))*((\s*[+]\s*((\()*(\s)*(!){0,2})"
			r"*(\s)*[A-Z](\s)*(\))*)*)?\s*$)")
		pattern_facts = re.compile(r"^=[A-Z]*\s*$")
		pattern_queries = re.compile(r"^\?[A-Z]*\s*$")

		fact = 1
		query = 1
		rule = 1

		rules = []
		for line1 in lines:
			line = line1.split("#", maxsplit=1)[0]
			if line == '':
				continue
			if line[0] == '=':
				len_facts = len(list(filter(None, re.findall("[A-Z]*", line))))
				self.facts = re.findall(r".", list(filter(None, re.findall("[A-Z]*", line)))[0]) if len_facts != 0 else []
				self.atoms = self.find_all_atoms(rules)
				fact -= 1
				if fact < 0:
					raise BaseException(f"{Color.WARNING}Error at line: {line1} - Facts were defined{Color.END}")
				if query <= 0:
					raise BaseException(f'{Color.WARNING}Error at line: {line1} - Facts must be defined before queries{Color.END}')
				if not Parser.check_atoms(self.atoms, line):
					raise BaseException(f'{Color.WARNING}Error at line: {line1} - Fact was not defined in rules{Color.END}')
				if pattern_facts.match(line) is None:
					raise BaseException(f'{Color.WARNING}Error at line: {line1} - Fact has bad format{Color.END}')
			elif line[0] == "?":
				len_queries = len(list(filter(None, re.findall("[A-Z]*", line))))
				self.queries = re.findall(r".", list(filter(None, re.findall("[A-Z]*", line)))[0]) if len_queries != 0 else []
				query -= 1
				if fact > 0:
					raise BaseException(f'{Color.WARNING}Error at line: {line1} - Facts were not defined{Color.END}')
				if not Parser.check_atoms(self.atoms, line):
					raise BaseException(f'{Color.WARNING}Error at line: {line1} - Queries was not defined in rules{Color.END}')
				if pattern_queries.match(line) is None:
					raise BaseException(f'{Color.WARNING}Error at line: {line1} - Query has bad format{Color.END}')
			else:
				self.rules.append(line)
				rule -= 1
				if fact <= 0:
					raise BaseException(f'{Color.WARNING}Error at line: {line1} - Rules must be defined before facts{Color.END}')
				if query <= 0:
					raise BaseException(f'{Color.WARNING}Error at line: {line1} - Rules must be defined before queries{Color.END}')
				if pattern_rules.match(line) is None:
					raise BaseException(f'{Color.WARNING}Error at line: {line1} - Rule has bad format{Color.END}')
				if not Parser.ft_check_parentheses(line):
					raise BaseException(f'{Color.WARNING}Error at line: {line1} - Rule has bad parentheses{Color.END}')
				else:
					rules.append(line)

		if fact > 0 or query > 0 or rule > 0:
			raise BaseException(f'{Color.WARNING}Miss rule or fact or query{Color.END}')
