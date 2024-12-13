import argparse
import yaml

# Custom Exceptions
class SyntaxError(Exception):
    pass

# Helper Functions
def parse_value(value, constants):
    if isinstance(value, list):
        return f'( {" ".join(parse_value(v, constants) for v in value)} )'
    elif isinstance(value, dict):
        return parse_dict(value, constants)
    elif isinstance(value, str) and value.startswith('${') and value.endswith('}'):
        return value  # Reference to a constant
    elif isinstance(value, (int, float, str)):
        # Check if value is a constant
        for const_name, const_value in constants.items():
            if const_value == value:
                return f'${{{const_name}}}'
        return str(value)
    else:
        raise SyntaxError(f"Unsupported value type: {value}")

def parse_dict(data, constants):
    result = ["begin"]
    for key, value in data.items():
        if not key.replace("_", "").isalnum():
            raise SyntaxError(f"Invalid key name: {key}")
        result.append(f" {key} := {parse_value(value, constants)};")
    result.append("end")
    return "\n".join(result)

def find_duplicates(data):
    """
    Traverse the YAML data to find values that are duplicated across different parts
    of the structure. Values in the same dictionary or list are not considered duplicates.
    """
    seen = {}
    constants = {}
    const_index = 1
    aliases = {}

    def traverse(value, current_path):
        nonlocal const_index
        if isinstance(value, list):
            # For lists, traverse each item and treat it as part of the current path
            for idx, item in enumerate(value):
                traverse(item, current_path + [f"[{idx}]"])
        elif isinstance(value, dict):
            # For dictionaries, traverse each key-value pair
            for k, v in value.items():
                traverse(v, current_path + [k])
        elif isinstance(value, (int, float, str)):
            # Check if the value is part of an alias (e.g., <<: *db_settings)
            value_path = tuple(current_path)  # Use the path as a tuple
            if value_path in aliases:
                return  # Skip if it's part of a reference
            if value in seen:
                if value not in constants:
                    constants[value] = f"constant_{const_index}"
                    const_index += 1
            else:
                seen[value] = True
                aliases[value_path] = f"constant_{const_index}"  # Track alias for later

    traverse(data, [])
    return constants

def replace_with_constants(data, constants):
    """
    Replace values in the YAML data with references to constants where applicable.
    """
    if isinstance(data, list):
        return [replace_with_constants(v, constants) for v in data]
    elif isinstance(data, dict):
        return {k: replace_with_constants(v, constants) for k, v in data.items()}
    elif isinstance(data, (int, float, str)) and data in constants:
        return f'${{{constants[data]}}}'
    return data

def convert_yaml_to_custom(input_path, output_path):
    with open(input_path, 'r') as yaml_file:
        yaml_data = yaml.safe_load(yaml_file)

    # Find duplicates and generate constants
    constants = find_duplicates(yaml_data)

    # Replace duplicate values with constants
    transformed_data = replace_with_constants(yaml_data, constants)

    with open(output_path, 'w') as output_file:
        # Write constants at the top
        for const_name, const_value in constants.items():
            output_file.write(f"{const_value}: {const_name}\n")

        # Write the main structure
        output_file.write("\n" + parse_dict(transformed_data, constants))

# CLI Integration
def main():
    parser = argparse.ArgumentParser(description="Convert YAML to custom configuration language.")
    parser.add_argument("--input", required=True, help="Path to the input YAML file.")
    parser.add_argument("--output", required=True, help="Path to the output configuration file.")
    args = parser.parse_args()

    try:
        convert_yaml_to_custom(args.input, args.output)
        print("Conversion completed successfully.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
