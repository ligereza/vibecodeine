import ast
from typing import List

def list_public_functions(source: str) -> List[str]:
    tree = ast.parse(source, mode='exec')
    public_function_signatures = []
    
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith('_'):
            args = ', '.join([
                *[f'{arg.arg}{"=" + ast.unparse(arg.annotation) if arg.annotation else ""}' for arg in node.args.posonlyargs],  # positional-only arguments
                *[f'{arg.arg}{"=" + ast.unparse(arg.annotation) if arg.annotation else ""}' for arg in node.args.args],  # positional arguments
                *([node.args.vararg.arg] if node.args.vararg else []),  # variable-length argument
                *[f'{kwarg.arg}{"=" + ast.unparse(kwarg.annotation) if kwarg.annotation else ""}' for kwarg in node.args.kwonlyargs],  # keyword-only arguments
            ])
            
            return_type = f': {ast.unparse(node.returns)}' if node.returns is not None else ''
            
            public_function_signatures.append(f"{node.name}({args}){return_type}")
    
    return public_function_signatures
