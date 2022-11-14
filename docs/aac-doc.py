# Copyright: (c) 2021, Daniel Schmidt <danischm@cisco.com>

import os
import re

import click
import ruamel.yaml
import yamale
from ruamel.yaml.comments import CommentedMap


ANNOTATIONS = [
    "name",
    "ref_name",
    "flatten",
    "hidden",
    "key",
    "ref_table",
    "description",
]


def load_yaml_file(path):
    data = CommentedMap()
    if os.path.isfile(path):
        with open(path, "r") as yaml_file:
            data_yaml = yaml_file.read()
            yaml = ruamel.yaml.YAML()
            data = list(yaml.load_all(data_yaml))
    return data


def add_comments(schema, schema_comments):
    for attr in schema.dict:
        comment_item = schema_comments[0].ca.items.get(attr)
        if comment_item:
            schema.dict[attr].comment = comment_item[2].value[1:].strip()
    for include in schema.includes:
        item = schema_comments[1][include]
        for attr in schema.includes[include].dict:
            comment_item = item.ca.items.get(attr)
            if comment_item:
                schema.includes[include].dict[attr].comment = (
                    comment_item[2].value[1:].strip()
                )


def load_schema(path):
    """Load a yamale schema and add annotations as attributes to schema elements."""
    schema = yamale.make_schema(path, parser="ruamel")
    schema_comments = load_yaml_file(path)
    for attr in schema.dict:
        comment_item = schema_comments[0].ca.items.get(attr)
        if comment_item:
            parse_annotations(schema.dict[attr], comment_item[2].value[1:].strip())
    for include in schema.includes:
        item = schema_comments[1][include]
        for attr in schema.includes[include].dict:
            comment_item = item.ca.items.get(attr)
            if comment_item:
                parse_annotations(
                    schema.includes[include].dict[attr],
                    comment_item[2].value[1:].strip(),
                )
    return schema


def parse_annotations(schema_item, comment):
    """Parse annotations from comments in schema yaml and add as attributes to respective schema elements."""
    for annotation in ANNOTATIONS:
        search_regex = "(?<=@{}\\().*?(?=\\))".format(annotation)
        match = re.search(search_regex, comment)
        if match:
            setattr(schema_item, annotation, match.group())


def read_schema_path(schema, path):
    path_elements = path.split(".")

    next_element = schema.includes[path_elements[0]]

    element = None
    name = ""

    if len(path_elements) == 1:
        return schema.dict[path_elements[0]], path_elements[0]

    for p in path_elements[1:]:
        element = next_element.dict[p]
        name = p
        if element.tag == "include":
            next_element = schema.includes[element.include_name]
        elif element.tag == "list":
            if element.validators[0].tag == "include":
                next_element = schema.includes[element.validators[0].include_name]
            else:
                next_element = element
        else:
            next_element = element

    return element, name


def expand_paths(schema, paths):
    new_paths = []
    for path in paths:
        element, _ = read_schema_path(schema, path)
        if element.tag == "include":
            for item in schema.includes[element.include_name].dict:
                new_paths.append(path + "." + item)
        if element.tag == "list":
            if element.validators[0].tag == "include":
                for item in schema.includes[element.validators[0].include_name].dict:
                    new_paths.append(path + "." + item)

    if len(new_paths) > 0:
        new_paths = expand_paths(schema, new_paths)

    paths.extend(new_paths)
    return paths


def parse_schema_type(element, name=""):
    result = None
    if element.tag == "str":
        args = []
        for arg, value in element.kwargs.items():
            args.append("{0}: {1}".format(arg, value))
        args_string = ", ".join(args)
        if len(args_string) > 0:
            result = "String[{0}]".format(args_string)
        else:
            result = "String"
    elif element.tag == "int":
        args = []
        for arg, value in element.kwargs.items():
            args.append("{0}: {1}".format(arg, value))
        args_string = ", ".join(args)
        if len(args_string) > 0:
            result = "Integer[{0}]".format(args_string)
        else:
            result = "Integer"
    elif element.tag == "num":
        args = []
        for arg, value in element.kwargs.items():
            args.append("{0}: {1}".format(arg, value))
        args_string = ", ".join(args)
        if len(args_string) > 0:
            result = "Number[{0}]".format(args_string)
        else:
            result = "Number"
    elif element.tag == "bool":
        result = "Boolean"
    elif element.tag == "null":
        result = "Null"
    elif element.tag == "enum":
        enum_list = ", ".join([str(e) for e in element.enums])
        result = "Choice[{0}]".format(enum_list)
    elif element.tag == "list":
        if element.validators[0].tag == "include":
            type = name
        else:
            type = parse_schema_type(element.validators[0], name)
        result = "List[{0}]".format(type)
    elif element.tag == "map":
        result = "Map"
    elif element.tag == "ip":
        result = "IP"
    elif element.tag == "mac":
        result = "MAC"
    elif element.tag == "regex":
        pattern = element.regexes[0].pattern
        pattern = pattern.replace("|", "\|")  # escape pipe in markdown
        result = "Regex[{0}]".format(pattern)
    elif element.tag == "include":
        result = "Class[{0}]".format(name)
    elif element.tag == "any":
        types = []
        for validator in element.validators:
            type = parse_schema_type(validator)
            if type is not None:
                types.append(type)
        result = " or ".join(types)

    return result


def parse_description(element):
    return getattr(element, "description", "")


def parse_mandatory(element):
    if element.is_required:
        return "Yes"
    else:
        return "No"


def get_default(defaults, path):
    path_elements = path.split(".")
    default_value = defaults["defaults"]
    for p in path_elements:
        if not isinstance(default_value, dict):
            break
        default_value = default_value.get(p)
        if default_value is None:
            default_value = ""
            break
    if isinstance(default_value, dict) or isinstance(default_value, list):
        return ""
    return default_value


def render_class(schema, defaults, class_path, paths):
    class_path_elements = class_path.split(".")
    parent = ".".join(class_path_elements[:-1])
    if parent:
        parent = " *({})*".format(parent)
    output = "\n### {0}{1}\n\n".format(class_path_elements[-1], parent)
    output += "Name | Type | Mandatory | Default | Description\n"
    output += "---|---|---|---|---\n"
    for path in paths:
        path_elements = path.split(".")
        cp = ".".join(path_elements[:-1])
        if class_path == cp:
            element, name = read_schema_path(schema, path)
            type = parse_schema_type(element, name)
            comment = parse_description(element)
            mandatory = parse_mandatory(element)
            default = get_default(defaults, path)
            output += "{0} | {1} | {2} | {3} | {4}".format(
                name, type, mandatory, default, comment
            ).strip()
            output += "\n"
    return output


def render_class_list(schema, defaults, class_paths, paths):
    output = "## Classes\n"
    for class_path in class_paths:
        output += render_class(schema, defaults, class_path, paths)
    return output


def render_diagram_path(element, path, mappings={}):
    result = ""
    path_elements = path.split(".")
    if path in mappings:
        name = mappings[path].split(".")[-1]
    else:
        name = path_elements[-1]
    if len(path_elements) > 1:
        parent_path = ".".join(path_elements[:-1])
        if parent_path in mappings:
            parent = mappings[parent_path].split(".")[-1]
        else:
            parent = path_elements[-2]
    else:
        parent = ""
    if element.is_required:
        mandatory = "+"
    else:
        mandatory = "-"
    if element.tag == "str":
        result = "{0} : {1}{2} Str\n".format(parent, mandatory, name)
    elif element.tag == "int":
        result = "{0} : {1}{2} Int\n".format(parent, mandatory, name)
    elif element.tag == "num":
        result = "{0} : {1}{2} Num\n".format(parent, mandatory, name)
    elif element.tag == "bool":
        result = "{0} : {1}{2} Bool\n".format(parent, mandatory, name)
    elif element.tag == "null":
        result = "{0} : {1}{2} Num\n".format(parent, mandatory, name)
    elif element.tag == "enum":
        result = "{0} : {1}{2} Enum\n".format(parent, mandatory, name)
    elif element.tag == "list":
        result = "{0} <-- {1}\n".format(parent, name)
        result += "{0} : {1}{2} List\n".format(parent, mandatory, name)
    elif element.tag == "map":
        pass
    elif element.tag == "ip":
        result = "{0} : {1}{2} IP\n".format(parent, mandatory, name)
    elif element.tag == "mac":
        result = "{0} : {1}{2} MAC\n".format(parent, mandatory, name)
    elif element.tag == "regex":
        result = "{0} : {1}{2} Str\n".format(parent, mandatory, name)
    elif element.tag == "include":
        result = "{0} *-- {1}\n".format(parent, name)
        result += "{0} : {1}{2} Dict\n".format(parent, mandatory, name)
    elif element.tag == "any":
        if element.validators[0].tag == "str":
            result = "{0} : {1}{2} Str\n".format(parent, mandatory, name)
        else:
            result = "{0} : {1}{2} Any\n".format(parent, mandatory, name)
    return result


def render_diagram_class(schema, defaults, class_path, paths, rendered_paths, mappings):
    output = ""
    for path in paths:
        path_elements = path.split(".")
        cp = ".".join(path_elements[:-1])
        if class_path == cp:
            current_path = []
            for idx, path_element in enumerate(path_elements):
                current_path.append(path_element)
                if idx == 0:
                    continue
                path_string = ".".join(current_path)
                if path_string in rendered_paths:
                    continue
                rendered_paths.append(path_string)
                element, name = read_schema_path(schema, path_string)
                output += render_diagram_path(element, ".".join(current_path), mappings)
    return output


def get_rename_mappings(class_paths):
    def next_name(c):
        index = 1
        while True:
            new_name = "{}_{}".format(c, index)
            if new_name not in classes:
                return new_name
            index += 1

    mappings = {}
    classes = []
    for class_path in class_paths:
        path_elements = class_path.split(".")
        c = path_elements[-1]
        if c in classes:
            new_name = next_name(c)
            classes.append(new_name)
            mappings[class_path] = ".".join(path_elements[:-1]) + "." + new_name
            continue
        classes.append(c)
    return mappings


def render_diagram(schema, defaults, class_paths, paths):
    output = "## Diagram\n\n"
    output += "```mermaid\n%%{init: {'themeVariables': {'nodeBorder': '#009688'}}}%%\nclassDiagram\n"
    rendered_paths = []
    mappings = get_rename_mappings(class_paths)
    for class_path in class_paths:
        output += render_diagram_class(
            schema, defaults, class_path, paths, rendered_paths, mappings
        )
    output += "```\n\n"
    return output


def extract_class_paths(schema, paths):
    class_paths = []
    schema_names = []
    for path in paths:
        path_elements = path.split(".")
        class_path = ".".join(path_elements[:-1])
        if len(path_elements) > 2:
            element, _ = read_schema_path(schema, class_path)
            schema_name = ""
            if element.tag == "include":
                schema_name = element.include_name
            elif element.tag == "list":
                schema_name = element.validators[0].include_name
            if schema_name and schema_name in schema_names:
                continue
            schema_names.append(schema_name)
        if class_path not in class_paths:
            class_paths.append(class_path)
    return class_paths


def render_doc(system, schema_path, objects_path, defaults_path):
    schema = load_schema(schema_path)
    objects = load_yaml_file(objects_path)[0]
    defaults = load_yaml_file(defaults_path)[0]

    for item in (
        objects["objects"]
        + objects.get("bootstrap_objects", [])
        + objects.get("leaf_objects", [])
        + objects.get("spine_objects", [])
        + objects.get("tenant_objects", [])
    ):
        template_path = os.path.join(
            ".",
            "templates",
            system,
            item["folder"],
            item["template"] + ".md",
        )
        rendered_path = os.path.join(
            ".",
            "model",
            system,
            item["folder"],
            item["template"] + ".md",
        )
        if os.path.isfile(template_path):
            paths = item.get("paths")
            paths = expand_paths(schema, paths)
            class_paths = extract_class_paths(schema, paths)
            output = ""
            output += render_diagram(schema, defaults, class_paths, paths)
            output += render_class_list(schema, defaults, class_paths, paths)

            with open(template_path, "r") as file:
                filedata = file.read()

            filedata = filedata.replace("{{ aac_doc }}", output)

            if not os.path.exists(os.path.dirname(rendered_path)):
                os.makedirs(os.path.dirname(rendered_path))
            with open(rendered_path, "w") as file:
                file.write(filedata)


schema = click.option(
    "-s",
    "--schema",
    type=click.Path(exists=True),
    help="Schema file.",
    required=True,
)


objects = click.option(
    "-o",
    "--objects",
    type=click.Path(exists=True),
    help="Objects file.",
    required=True,
)


defaults = click.option(
    "-d",
    "--defaults",
    type=click.Path(exists=True),
    help="Defaults file.",
    required=True,
)


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
def main():
    """Render aac doc files."""
    pass


@main.command()
@schema
@objects
@defaults
def apic(schema, objects, defaults):
    """Render APIC aac doc files."""
    render_doc("apic", schema, objects, defaults)


@main.command()
@schema
@objects
@defaults
def mso(schema, objects, defaults):
    """Render MSO aac doc files."""
    render_doc("mso", schema, objects, defaults)


if __name__ == "__main__":
    main()
