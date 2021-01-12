import re
from .node import ConnectorType, ConnectorNode, AtomNode, NegativeNode
from .rpn_parser import ImplyType, OPERATORS
from .color import Color

LST_OP = {'+': ConnectorType.AND, '|': ConnectorType.OR, '^': ConnectorType.XOR}


class Validation:
	def __init__(self, left, right):
		self.left = left
		self.right = right

	def __repr__(self):
		return f'.left {self.left} .right {self.right}'

	def validate(self):
		left_res = self.left.decide()
		right_res = self.right.decide()
		if left_res is True and right_res is False:
			raise BaseException(f'{Color.WARNING}ERROR: {self} (True => False) is invalid{Color.END}')


class Tree:
	def __init__(self):
		self.atoms = {}
		self.connectors = []
		self.valid_data = []
		self.root_node = ConnectorNode(ConnectorType.AND, self)
		self.root_node.is_root = True

	def init_atom(self, atom_name: str):
		atom = self.atoms.get(atom_name)
		if atom is None:
			atom = AtomNode(atom_name, self)
			self.atoms[atom_name] = atom
			self.root_node.add_operand(atom)

		return atom

	def create_connect(self, type1: ConnectorType):
		return ConnectorNode(type1, self)

	def set_atom_state(self, atom_name: str, value):
		atom = self.atoms.get(atom_name)
		if atom is None:
			raise BaseException(f"{Color.WARNING}{atom_name} doesn't have any known atom{Color.END}")
		atom.state = value
		if value is True:
			atom.state_fixed = True

	def decide_query(self, query: str):
		atom = self.atoms.get(query)
		if atom is None:
			raise BaseException(f"{Color.WARNING}[ERROR] The query {query} doesn't know any atoms{Color.END}")
		res = atom.decide()
		if res is None:
			atom.set_state(False, True)
			res = False

		self.check_validation()
		return res

	def check_validation(self):
		for valid in self.valid_data:
			valid.validate()


class RPNTree(Tree):
	def __init__(self, atoms: list, rpn_rules: list, facts: list):
		super(RPNTree, self).__init__()

		self.init_atoms_list(atoms)
		self.set_atoms_state(rpn_rules, facts)
		self.set_relations(rpn_rules)

	def init_atoms_list(self, atoms: list):
		for atom in atoms:
			self.atoms[atom] = self.init_atom(atom)

	def set_atoms_state(self, rpn_rules: list, facts: list):
		conclusion_atoms = []
		for atom in rpn_rules:
			conclusion_atoms += re.findall(r'[A-Z]', atom.right)
			if atom.type is ImplyType.EQUAL:
				conclusion_atoms += re.findall(r'[A-Z]', atom.left)

		conclusion_atoms = list(set(conclusion_atoms))
		for atom in conclusion_atoms:
			self.set_atom_state(atom, None)
		for atom in facts:
			self.set_atom_state(atom, True)

	def set_relations(self, rpn_rules: list):
		if len(self.atoms) is 0:
			raise BaseException(f'{Color.WARNING}Tree is empty{Color.END}')
		for rule in rpn_rules:
			left = self.get_relations(rule.left)
			right = self.get_relations(rule.right)
			imply_connect = self.create_connect(ConnectorType.IMPLY)
			right.add_child(imply_connect)
			imply_connect.add_operand(left)
			self.valid_data.append(Validation(left, right))
			if rule.type is ImplyType.EQUAL:
				imply_connect1 = self.create_connect(ConnectorType.IMPLY)
				left.add_child(imply_connect1)
				imply_connect1.add_operand(right)
				self.valid_data.append(Validation(right, left))

	def get_relations(self, rule: str):
		stack = []
		for ch in rule:
			if ch not in OPERATORS:
				stack.append(self.atoms[ch])
			elif ch == '!':
				child = stack.pop()
				connector_not = NegativeNode(child)
				child.operand_parents.append(connector_not)
				stack.append(connector_not)
			else:
				pop0 = stack.pop()
				pop1 = stack.pop()
				if isinstance(pop0, ConnectorNode) and pop0.type is LST_OP[ch]:
					pop0.add_operand(pop1)
					new_connector = pop0
					self.connectors.pop()
				elif isinstance(pop1, ConnectorNode) and pop1.type is LST_OP[ch]:
					pop1.add_operand(pop0)
					new_connector = pop1
					self.connectors.pop()
				else:
					connector_ch = self.create_connect(LST_OP[ch])
					connector_ch.add_operands([pop0, pop1])
					new_connector = connector_ch
				self.connectors.append(new_connector)
				stack.append(new_connector)

		return stack.pop()



