from enum import Enum


class ConnectorType(Enum):
	OR = '|'
	AND = '&'
	XOR = '^'
	IMPLY = '=>'


class Node:
	def __init__(self, tree):
		self.children = []
		self.operand_parents = []
		self.visited = False
		self.state = False
		self.state_fixed = False
		self.tree = tree

	def add_child(self, child):
		if child not in self.children:
			self.children.append(child)

	def set_state(self, state, is_fixed: bool):
		if self.state_fixed is True and is_fixed is True and self.state is not None and self.state != state:
			raise BaseException(f'Node received two different states')

		self.state = state
		self.state_fixed = is_fixed
		return state

	def decide(self):
		if self.visited is True:
			return self.state

		state = None
		if self.state is not None:
			state = self.state
			if self.state_fixed is True:
				return state

		fixed_ret = []
		unfixed_ret = []
		f, u = self.decide_complex(self.children, False)
		fixed_ret.extend(f)
		unfixed_ret.extend(u)

		self.decide_complex(self.operand_parents, True)

		ret = fixed_ret if len(fixed_ret) is not 0 else unfixed_ret
		if len(ret) is not 0:
			if True in ret:
				state = True
			else:
				state = False

		is_fixed = True if len(fixed_ret) is not 0 else False
		need_reverse = True
		if state is None:
			need_reverse = False
			state = self.state

		if state is not None:
			if isinstance(self, NegativeNode) and need_reverse:
				state = not state if state is not None else None
			return self.set_state(state, is_fixed)
		return None

	def decide_complex(self, children: list, check_parents: bool):
		self.visited = True
		fixed_res = []
		unfixed_res = []
		for child in children:
			if check_parents and isinstance(child, ConnectorNode) and child.type is not ConnectorType.AND:
				continue
			r = child.decide()
			if isinstance(self, NegativeNode) and isinstance(child, ConnectorNode) \
					and child.type is ConnectorType.IMPLY and not check_parents:
				r = not r if r is not None else None
			if r is not None and child.state_fixed:
				fixed_res.append(r)
			elif r is not None:
				unfixed_res.append(r)
		self.visited = False
		return fixed_res, unfixed_res


class ConnectorNode(Node):
	def __init__(self, connector_type: ConnectorType, tree):
		super(ConnectorNode, self).__init__(tree)
		self.type = connector_type
		self.operands = []
		self.state = None
		self.is_root = False

	def __repr__(self):
		return f'{self.type.value} .operands: {self.operands}'

	def set_state(self, state, is_fixed: bool):
		super(ConnectorNode, self).set_state(state, is_fixed)

		if self.type is ConnectorType.AND and state is True:
			for op in self.operands:
				op.set_state(state, is_fixed)
		return state

	def add_operand(self, operand: Node):
		if self.type is ConnectorType.IMPLY and self.operands.__len__() > 0:
			raise BaseException("An imply connection must only have one operand")
		self.operands.append(operand)
		if self.is_root is False and self.type is not ConnectorType.IMPLY and self not in operand.operand_parents:
			operand.operand_parents.append(self)

	def add_operands(self, operands: list):
		[self.add_operand(op) for op in operands]

	def decide(self):
		if self.visited:
			return self.state

		self.visited = True
		if self.type is ConnectorType.IMPLY:
			operand_state = self.operands[0].decide()
			self.set_state(operand_state, self.operands[0].state_fixed)
			self.visited = False
			return operand_state

		res = None
		none_state = False
		fixed_operands = False

		for operand in self.operands:
			operand_state = operand.decide()
			if operand.state_fixed is True:
				fixed_operands = True
			if operand_state is None:
				none_state = True
				continue
			elif res is None:
				res = operand_state
			elif self.type is ConnectorType.AND:
				res &= operand_state
			elif self.type is ConnectorType.OR:
				res |= operand_state
			elif self.type is ConnectorType.XOR:
				res ^= operand_state

		self.visited = False
		if none_state and ((self.type is ConnectorType.AND and res is True) or
							(self.type is ConnectorType.OR and res is False) or
							(self.type is ConnectorType.XOR)):
			return None

		if res is not None:
			return self.set_state(res, fixed_operands)

		return super(ConnectorNode, self).decide()


class NegativeNode(Node):
	def __init__(self, child: Node):
		if child is None:
			raise BaseException(f'Negative Node has to have child')
		super(NegativeNode, self).__init__(None)
		self.state = None
		self.add_child(child)

	def __repr__(self):
		return f'{self.children[0]}'

	def add_child(self, child: Node):
		super(NegativeNode, self).add_child(child)
		child.operand_parents.append(self)

	def set_state(self, state, is_fixed: bool):
		res = super(NegativeNode, self).set_state(state, is_fixed)
		self.children[0].set_state(not res if res is not None else None, is_fixed)
		return res


class AtomNode(Node):
	def __init__(self, name: str, tree):
		super(AtomNode, self).__init__(tree)
		self.name = name

	def __repr__(self):
		return f'{self.name}'

	def __eq__(self, other: str):
		return isinstance(other, AtomNode) and self.name == other.name
