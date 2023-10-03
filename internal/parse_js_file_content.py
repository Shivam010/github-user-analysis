import re


def parse_js_file_content(fname: str, content: str):
    information = {
        "comments": [],
        "functions": [],
        "classes": [],
        "arrow_functions": [],
        "global_variables": [],
        "struct_types": [],
        "constants": [],
        "type_definitions": [],
        "components": [],
        "hooks": [],
    }

    is_jsx = fname.endswith((".tsx", ".jsx"))

    lines = content.splitlines()
    for line_number, line in enumerate(lines, start=1):
        # Extract Comments
        comments_match = re.findall(r"\/\/(.+)|\/\*(.+)\*\/", line)
        if comments_match:
            information["comments"].extend(
                [
                    {"text": c[0] if c[0] else c[1], "line_number": line_number}
                    for c in comments_match
                ]
            )

        # Extract Functions
        functions_match = re.findall(r"\bfunction\s+([a-zA-Z_$][\w$]*)\s*\(", line)
        information["functions"].extend(
            [{"name": func, "line_number": line_number} for func in functions_match]
        )

        # Extract Classes
        classes_match = re.findall(r"\bclass\s+([a-zA-Z_$][\w$]*)", line)
        information["classes"].extend(
            [{"name": class_, "line_number": line_number} for class_ in classes_match]
        )

        # Extract Arrow Functions
        arrow_functions_match = re.findall(r"([a-zA-Z_$][\w$]*)\s*=\s*\(\)\s*=>", line)
        information["arrow_functions"].extend(
            [
                {"name": func, "line_number": line_number}
                for func in arrow_functions_match
            ]
        )

        # Extract Global Variables
        global_variables_match = re.findall(r"\bvar\s+([a-zA-Z_$][\w$]*)\s*=", line)
        information["global_variables"].extend(
            [
                {"name": var, "line_number": line_number}
                for var in global_variables_match
            ]
        )

        # Extract Struct Types (Assuming struct is defined similar to a class)
        struct_types_match = re.findall(r"\bstruct\s+([a-zA-Z_$][\w$]*)", line)
        information["struct_types"].extend(
            [
                {"name": struct, "line_number": line_number}
                for struct in struct_types_match
            ]
        )

        # Extract Constants
        constants_match = re.findall(r"\bconst\s+([a-zA-Z_$][\w$]*)\s*=", line)
        information["constants"].extend(
            [{"name": const, "line_number": line_number} for const in constants_match]
        )

        # Extract Type Definitions
        type_definitions_match = re.findall(
            r"\b(?:type|interface)\s+([a-zA-Z_$][\w$]*)", line
        )
        information["type_definitions"].extend(
            [
                {"name": type_def, "line_number": line_number}
                for type_def in type_definitions_match
            ]
        )

        # Extract Components for TSX and JSX files
        if is_jsx:
            components_match = re.findall(
                r"\b(?:export\s+default\s+(?:async\s+)?+(?:function|const|class)\s+([A-Z_$][\w$]*))",
                line,
            )

            information["components"].extend(
                [
                    {"name": component, "line_number": line_number}
                    for component in components_match
                ]
            )

    if is_jsx:
        # Check for hooks in functions
        for func in information["functions"]:
            fname = func["name"]
            if fname.startswith("use"):
                information["hooks"].append(func)

        # Check for hooks in arrow functions
        for func in information["arrow_functions"]:
            fname = func["name"]
            if fname.startswith("use"):
                information["hooks"].append(func)

        # if components could not be extracted from the file
        # Check functions and arrow functions and Class for Capitalized (Titled) names

        # First check functions
        if len(information["components"]) == 0:
            for func in information["functions"]:
                fname = func["name"]
                if len(fname) > 0 and (fname[0] >= "A" and fname[0] <= "Z"):
                    information["components"].append(func)

        # then check arrow functions
        if len(information["components"]) == 0:
            for func in information["arrow_functions"]:
                fname = func["name"]
                if len(fname) > 0 and (fname[0] >= "A" and fname[0] <= "Z"):
                    information["components"].append(func)

        # then check classes
        if len(information["components"]) == 0:
            for cls in information["classes"]:
                fname = cls["name"]
                if len(fname) > 0 and (fname[0] >= "A" and fname[0] <= "Z"):
                    information["components"].append(cls)

    return information


def convert_to_plain_text(data):
    result = []

    for file_info in data:
        file_name = file_info.get("path", "Unknown File")
        result.append(f"{file_name} file contain:")

        info = file_info.get("info", {})
        for category, items in info.items():
            if items:
                names = ""
                # result.append(f"{category}:")
                for item in items:
                    line_number = item.get("line_number", "")
                    name = item.get("name", "")
                    if name and line_number:
                        names += f"{name} at line {line_number}, "
                if names and len(names) > 1:
                    result.append(f"  {category}: {names[:len(names)-2]}")

    return "\n".join(result)
