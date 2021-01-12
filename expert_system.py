# для цветного вывода на консоль в Windows
import ctypes
import argparse
from utils.parser import Parser
from utils.tree import RPNTree
from utils.color import Color

kernel32 = ctypes.windll.kernel32
kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)


def result(parser: Parser):
	tree = RPNTree(parser.atoms, parser.rpn_rules, parser.facts)
	results = {}
	for query in parser.queries:
		results[query] = tree.decide_query(query)
		color = Color.GREEN if results[query] is True else Color.RED
		print(f'{color}{query} => {results[query]}{Color.END}')


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("data", type=str, help='The file of rules, facts and queries')
	args = parser.parse_args()

	try:
		with open(args.data) as file:
			data = file.readlines()
		parser1 = Parser(data)
		result(parser1)

	except (Exception, BaseException) as e:
		print(e)
		exit(1)
