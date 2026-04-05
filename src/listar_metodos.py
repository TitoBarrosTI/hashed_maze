import ast
import sys

if len(sys.argv) < 2:
    print("Uso: python listar_metodos.py <arquivo.py>")
    sys.exit(1)

arquivo = sys.argv[1]

with open(arquivo, "r", encoding="utf-8") as f:
    tree = ast.parse(f.read())

funcoes = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

print(f"Métodos encontrados em {arquivo}:")
for i, nome in enumerate(funcoes, 1):
    print(f"{i}. {nome}")