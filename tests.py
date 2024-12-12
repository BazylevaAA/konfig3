import unittest
import os
from main import convert_yaml_to_custom, generate_constants, parse_dict, SyntaxError  # Импортируйте ваши функции


class TestYAMLConversion(unittest.TestCase):
    def test_conversion(self):
        input_yaml = "test_input.yaml"
        output_file = "test_output.txt"

        # Пример YAML содержимого
        yaml_content = """
        example_key:
            - value1
            - value2
        another_key: 42
        """

        # Сохраняем тестовый YAML
        with open(input_yaml, 'w') as f:
            f.write(yaml_content)

        # Запускаем конвертацию
        convert_yaml_to_custom(input_yaml, output_file)

        # Проверяем, что файл вывода существует
        self.assertTrue(os.path.exists(output_file))

        with open(output_file, 'r') as f:
            output_content = f.read()

        # Проверяем, что в выходном файле присутствуют константы и основная структура
        self.assertIn("constant_1: ( value1 value2 )", output_content)
        self.assertIn("another_key := 42;", output_content)

        # Убираем временные файлы
        os.remove(input_yaml)
        os.remove(output_file)


class TestGenerateConstants(unittest.TestCase):
    def test_generate_constants(self):
        data = {
            "key1": [1, 2, 3],
            "key2": {"nested_key": 10},
        }

        constants = generate_constants(data)

        # Проверяем, что константы сгенерированы правильно
        self.assertIn("constant_1", constants)
        self.assertIn("constant_2", constants)
        self.assertEqual(constants["constant_1"], [1, 2, 3])
        self.assertEqual(constants["constant_2"], {"nested_key": 10})


class TestInvalidKeyName(unittest.TestCase):
    def test_invalid_key_name(self):
        data = {
            "invalid key": "value"
        }

        with self.assertRaises(SyntaxError):
            parse_dict(data)


class TestEmptyYAML(unittest.TestCase):
    def test_empty_yaml(self):
        data = {}

        constants = generate_constants(data)
        output = parse_dict(data)

        # Убедимся, что в пустом YAML не генерируются константы и нет данных
        self.assertEqual(constants, {})
        self.assertEqual(output, "begin\nend")


class TestConstantReferences(unittest.TestCase):
    def test_constant_reference(self):
        data = {
            "key1": "${constant_1}",
            "key2": 42
        }

        constants = generate_constants(data)
        output = parse_dict(data)

        # Проверяем, что ссылку на константу заменяет правильное имя
        self.assertIn("${constant_1}", output)
        self.assertIn("key2 := 42;", output)


if __name__ == "__main__":
    unittest.main()
