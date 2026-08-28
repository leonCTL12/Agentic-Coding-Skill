from tree_sitter import Language, Parser, Query
import tree_sitter_c_sharp as tscsharp
from .base import LanguagePlugin, _matches, _fill_docs_from_siblings

_LANGUAGE = Language(tscsharp.language())
_PARSER = Parser(_LANGUAGE)

_TYPE_QUERIES = (
    ("class_declaration", "class"),
    ("interface_declaration", "interface"),
    ("enum_declaration", "enum"),
    ("struct_declaration", "struct"),
    ("record_declaration", "class"),
)

# enum_declaration uses enum_member_declaration_list, not declaration_list.
_METHOD_PARENTS = (
    "class_declaration",
    "interface_declaration",
    "struct_declaration",
    "record_declaration",
)


def _parse(source: bytes):
    return _PARSER.parse(source)


def _text(node) -> str:
    return node.text.decode("utf-8", errors="replace")


class CSharpPlugin(LanguagePlugin):
    extensions = (".cs",)

    def extract_skeleton(self, source: bytes) -> list[dict]:
        tree = _parse(source)
        results = []

        for node_type, kind in _TYPE_QUERIES:
            q = Query(_LANGUAGE, f"({node_type} name: (identifier) @name) @def")
            for _, m in _matches(q, tree.root_node):
                results.append({
                    "type": kind,
                    "name": _text(m["name"]),
                    "line": m["name"].start_point[0] + 1,
                    "parent": None,
                    "params": "",
                })

        for parent_type in _METHOD_PARENTS:
            q = Query(_LANGUAGE, f"""
                ({parent_type}
                    name: (identifier) @class_name
                    body: (declaration_list
                        (method_declaration
                            name: (identifier) @method_name
                            parameters: (parameter_list) @params)))
            """)
            for _, m in _matches(q, tree.root_node):
                results.append({
                    "type": "method",
                    "name": _text(m["method_name"]),
                    "line": m["method_name"].start_point[0] + 1,
                    "parent": _text(m["class_name"]),
                    "params": _text(m["params"]),
                })

            q = Query(_LANGUAGE, f"""
                ({parent_type}
                    name: (identifier) @class_name
                    body: (declaration_list
                        (constructor_declaration
                            name: (identifier) @ctor_name
                            parameters: (parameter_list) @params)))
            """)
            for _, m in _matches(q, tree.root_node):
                results.append({
                    "type": "method",
                    "name": _text(m["ctor_name"]),
                    "line": m["ctor_name"].start_point[0] + 1,
                    "parent": _text(m["class_name"]),
                    "params": _text(m["params"]),
                })

        for item in results:
            item.setdefault("doc", "")
        _fill_docs_from_siblings(results, tree.root_node, _LANGUAGE, [
            "(class_declaration name: (identifier) @name) @def",
            "(interface_declaration name: (identifier) @name) @def",
            "(enum_declaration name: (identifier) @name) @def",
            "(struct_declaration name: (identifier) @name) @def",
            "(record_declaration name: (identifier) @name) @def",
            "(method_declaration name: (identifier) @name) @def",
        ])

        results.sort(key=lambda x: x["line"])
        return results

    def extract_symbol_source(self, source: bytes, name: str) -> tuple[str, int] | None:
        tree = _parse(source)
        for q_str in [
            "(class_declaration name: (identifier) @name) @def",
            "(interface_declaration name: (identifier) @name) @def",
            "(enum_declaration name: (identifier) @name) @def",
            "(struct_declaration name: (identifier) @name) @def",
            "(record_declaration name: (identifier) @name) @def",
            "(method_declaration name: (identifier) @name) @def",
            "(constructor_declaration name: (identifier) @name) @def",
        ]:
            for _, m in _matches(Query(_LANGUAGE, q_str), tree.root_node):
                if _text(m["name"]) == name:
                    node = m["def"]
                    return source[node.start_byte:node.end_byte].decode("utf-8", errors="replace"), node.start_point[0] + 1
        return None

    def extract_calls_in_function(self, source: bytes, fn_name: str) -> list[str]:
        tree = _parse(source)
        fn_node = self._find_function_node(tree, fn_name)
        if fn_node is None:
            return []
        calls = set()
        q = Query(_LANGUAGE, """
            (invocation_expression function: [
                (identifier) @called
                (generic_name (identifier) @called)
                (member_access_expression name: [
                    (identifier) @called
                    (generic_name (identifier) @called)
                ])
            ])
        """)
        for _, m in _matches(q, fn_node):
            calls.add(_text(m["called"]))
        q = Query(_LANGUAGE, """
            (object_creation_expression type: [
                (identifier) @called
                (generic_name (identifier) @called)
                (qualified_name (identifier) @called)
            ])
        """)
        for _, m in _matches(q, fn_node):
            calls.add(_text(m["called"]))
        return sorted(calls)

    def extract_symbol_usages(self, source: bytes, name: str) -> list[dict]:
        tree = _parse(source)
        usages = []
        seen = set()
        q = Query(_LANGUAGE, f'((identifier) @name (#eq? @name "{name}"))')
        for _, m in _matches(q, tree.root_node):
            node = m["name"]
            key = (node.start_point[0], node.start_point[1])
            if key not in seen:
                seen.add(key)
                usages.append({"line": node.start_point[0] + 1, "col": node.start_point[1]})
        usages.sort(key=lambda x: (x["line"], x["col"]))
        return usages

    def extract_imports(self, source: bytes) -> list[dict]:
        tree = _parse(source)
        results = []
        q = Query(_LANGUAGE, "(using_directive) @imp")
        for _, m in _matches(q, tree.root_node):
            node = m["imp"]
            results.append({
                "line": node.start_point[0] + 1,
                "text": _text(node).strip(),
            })
        results.sort(key=lambda x: x["line"])
        return results

    def compute_complexity(self, source: bytes, fn_name: str) -> dict | None:
        tree = _parse(source)
        fn_node = self._find_function_node(tree, fn_name)
        if fn_node is None:
            return None

        branch_map = {
            "if_statement": "if",
            "for_statement": "for",
            "foreach_statement": "foreach",
            "while_statement": "while",
            "do_statement": "do_while",
            "catch_clause": "catch",
            "switch_section": "case",
            "conditional_expression": "ternary",
        }
        counts: dict[str, int] = {}

        def walk(node):
            if node.type in branch_map:
                label = branch_map[node.type]
                counts[label] = counts.get(label, 0) + 1
            elif node.type == "binary_expression":
                for child in node.children:
                    if child.type in ("&&", "||"):
                        counts[child.type] = counts.get(child.type, 0) + 1
            for child in node.children:
                walk(child)

        walk(fn_node)
        total = 1 + sum(counts.values())
        return {"total": total, "breakdown": counts}

    def extract_variables(self, source: bytes, fn_name: str) -> list[dict]:
        tree = _parse(source)
        fn_node = self._find_function_node(tree, fn_name)
        if fn_node is None:
            return []

        results = []
        seen = set()

        def _add(name, line, var_type="", kind="local"):
            if name not in seen:
                seen.add(name)
                results.append({"name": name, "line": line, "type": var_type, "kind": kind})

        for child in fn_node.children:
            if child.type == "parameter_list":
                for param in child.children:
                    if param.type == "parameter":
                        type_text = ""
                        id_node = None
                        for sub in param.children:
                            if sub.type == "identifier":
                                id_node = sub
                            elif sub.type not in (",", "(", ")", "this", "params", "ref", "out", "in"):
                                type_text = _text(sub)
                        if id_node:
                            _add(_text(id_node), id_node.start_point[0] + 1,
                                 var_type=type_text, kind="parameter")
                break

        def walk(node):
            if node.type == "local_declaration_statement":
                for child in node.children:
                    if child.type == "variable_declaration":
                        type_text = ""
                        type_node = child.child_by_field_name("type")
                        if type_node:
                            type_text = _text(type_node)
                        for sub in child.children:
                            if sub.type == "variable_declarator":
                                name_node = sub.child_by_field_name("name") or next(
                                    (c for c in sub.children if c.type == "identifier"), None)
                                if name_node:
                                    _add(_text(name_node), name_node.start_point[0] + 1,
                                         var_type=type_text)
            elif node.type == "foreach_statement":
                type_node = node.child_by_field_name("type")
                left = node.child_by_field_name("left")
                if left and left.type == "identifier":
                    type_text = _text(type_node) if type_node else ""
                    _add(_text(left), left.start_point[0] + 1,
                         var_type=type_text, kind="loop_var")
            for child in node.children:
                walk(child)

        for child in fn_node.children:
            if child.type in ("block", "arrow_expression_clause"):
                walk(child)

        return results

    def check_syntax(self, source: bytes) -> bool:
        return _parse(source).root_node.has_error

    def _find_function_node(self, tree, fn_name: str):
        for q_str in [
            "(method_declaration name: (identifier) @name) @def",
            "(constructor_declaration name: (identifier) @name) @def",
        ]:
            for _, m in _matches(Query(_LANGUAGE, q_str), tree.root_node):
                if _text(m["name"]) == fn_name:
                    return m["def"]
        return None

    def _get_parser(self):
        return _PARSER

    def _get_language(self):
        return _LANGUAGE
