import ast

from microchain.engine.function import Function, FunctionResult

class Engine:
    def __init__(self, state=dict()):
        self.state = state
        self.functions = dict()
    
    def register(self, function):
        self.functions[function.name] = function
        function.bind(self.state)

    def execute(self, command):
        try:
            tree = ast.parse(command)
        except SyntaxError:
            return FunctionResult.ERROR, f"Error: syntax error in command {command}"
        
        if len(tree.body) != 1:
            return FunctionResult.ERROR, f"Error: unknown command {command}"

        if not isinstance(tree.body[0], ast.Expr):
            return FunctionResult.ERROR, f"Error: unknown command {command}"

        if not isinstance(tree.body[0].value, ast.Call):
            return FunctionResult.ERROR, f"Error: the command {command} must be a function call"
        
        if not isinstance(tree.body[0].value.func, ast.Name):
            return FunctionResult.ERROR, f"Error: the command {command} must be a function call"

        function_name = tree.body[0].value.func.id
        function_args = tree.body[0].value.args

        for arg in function_args:
            if not isinstance(arg, ast.Constant):
                return FunctionResult.ERROR, f"Error: the command {command} must be a function call, you cannot use variables"

        function_args = [arg.value for arg in function_args]

        if function_name not in self.functions:
            return FunctionResult.ERROR, f"Error: unknown command {command}"
        
        if len(function_args) != len(self.functions[function_name].args):
            return FunctionResult.ERROR, self.functions[function_name].error()

        return self.functions[function_name](function_args, self.state)
            
    
    def help(self):
        return "\n".join([f.help for f in self.functions.values()])
