import argparse
import yaml


# Custom Exceptions
class SyntaxError(Exception):
    pass


# Helper Functions
def parse_value(value):
    if isinstance(value, list):
        return f'( {" ".join(map(str, value))} )'
    elif isinstance(value, dict):
        return parse_dict(value)
    elif isinstance(value, str) and value.startswith('${') and value.endswith('}'):
        return value  # Reference to a constant
    elif isinstance(value, (int, float, str)):
        return str(value)
    else:
        raise SyntaxError(f"Unsupported value type: {value}")


def parse_dict(data):
    result = ["begin"]
    for key, value in data.items():
        if not key.replace("_", "").isalnum():
            raise SyntaxError(f"Invalid key name: {key}")
        result.append(f" {key} := {parse_value(value)};")
    result.append("end")
    return "\n".join(result)


def generate_constants(data):
    constants = {}
    reverse_lookup = {}

    def traverse(value):
        if isinstance(value, (list, dict)):
            serialized = yaml.dump(value, default_flow_style=False)  # Используем более читабельный стиль
            if serialized not in reverse_lookup:
                reverse_lookup[serialized] = f"constant_{len(reverse_lookup) + 1}"
                constants[reverse_lookup[serialized]] = value
            return f"${{{reverse_lookup[serialized]}}}"
        elif isinstance(value, (int, float, str)):
            return value
        return value

    for key, value in data.items():
        traverse(value)

    return constants


def convert_yaml_to_custom(input_path, output_path):
    with open(input_path, 'r') as yaml_file:
        yaml_data = yaml.safe_load(yaml_file)

    constants = generate_constants(yaml_data)

    with open(output_path, 'w') as output_file:
        # Запись констант в начале
        for const_name, const_value in constants.items():
            output_file.write(f"{const_name}: {parse_value(const_value)}\n")

        # Запись основной структуры данных
        output_file.write("\n" + parse_dict(yaml_data))


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
