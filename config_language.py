import argparse
import re
import xml.etree.ElementTree as ET


class ConfigParser:
    def __init__(self, file_content):
        self.content = file_content
        self.position = 0
        self.constants = {}  # Хранилище для констант

    def parse(self):
        return self.parse_blocks()

    def parse_blocks(self):
        blocks = []
        while self.position < len(self.content):
            line = self.content[self.position].strip()
            if line.endswith(";") or line.startswith("{") or ":=" in line:
                blocks.append(self.parse_assignment(line))
            else:
                self.error(f"Unexpected syntax: {line}")
            self.position += 1
        return blocks

    def parse_assignment(self, line):
        match = re.match(r"([a-zA-Z][_a-zA-Z0-9]*)\s*:=\s*(.+);?", line)
        if match:
            name, value = match.groups()
            if value.strip() == "{":  # Если начинается с '{', это словарь
                self.position += 1
                dictionary = self.parse_dictionary()
                self.constants[name] = dictionary
                return {"type": "assignment", "name": name, "value": dictionary}
            elif value.strip().startswith("|") and value.strip().endswith("|"):  # Константное выражение
                const_name = value.strip()[1:-1]
                if const_name in self.constants:
                    self.constants[name] = self.constants[const_name]
                    return {"type": "assignment", "name": name, "value": self.constants[const_name]}
                else:
                    self.error(f"Undefined constant: {const_name}")
            else:
                self.constants[name] = self.parse_value(value.strip())
                return {"type": "assignment", "name": name, "value": self.constants[name]}
        else:
            self.error(f"Invalid assignment syntax: {line}")

    def parse_dictionary(self):
        dictionary = {}
        while self.position < len(self.content):
            line = self.content[self.position].strip()
            if line in ("}", "};", "},"):  # Конец словаря
                break
            match = re.match(r"([a-zA-Z][_a-zA-Z0-9]*)\s*=>\s*(.+),?", line)
            if match:
                key, value = match.groups()
                value = value.rstrip(",")  # Убираем запятую в конце значения
                dictionary[key] = self.parse_value(value.strip())
            else:
                self.error(f"Invalid dictionary syntax: {line}")
            self.position += 1
        return dictionary

    def parse_value(self, value):
        value = value.rstrip(";")
        if re.match(r"^\d+$", value):  # Числа
            return int(value)
        elif re.match(r"^\[\[.*\]\]$", value):  # Строки
            return value[2:-2]  # Убираем [[ и ]]
        elif value.startswith("|") and value.endswith("|"):  # Константное выражение
            const_name = value[1:-1]
            if const_name in self.constants:
                return self.constants[const_name]
            else:
                self.error(f"Undefined constant: {const_name}")
        elif value.strip() == "{":  # Вложенный словарь
            self.position += 1
            return self.parse_dictionary()
        else:
            self.error(f"Invalid value: {value}")

    def error(self, message):
        raise SyntaxError(message)


class ConfigToXML:
    @staticmethod
    def convert(data):
        root = ET.Element("config")
        for block in data:
            if block["type"] == "assignment":
                const_elem = ET.SubElement(root, "constant", name=block["name"])
                if isinstance(block["value"], dict):
                    ConfigToXML.add_dictionary(const_elem, block["value"])
                else:
                    const_elem.text = str(block["value"])
        return ET.tostring(root, encoding="unicode")

    @staticmethod
    def add_dictionary(parent, dictionary):
        """Рекурсивно добавляет словари в XML."""
        dict_elem = ET.SubElement(parent, "dictionary")
        for key, value in dictionary.items():
            entry = ET.SubElement(dict_elem, "entry", key=key)
            if isinstance(value, dict):  # Рекурсия для вложенных словарей
                ConfigToXML.add_dictionary(entry, value)
            else:
                entry.text = str(value)

    @staticmethod
    def format_xml(xml_string):
        """Форматирует XML с отступами для читаемости."""
        import xml.dom.minidom
        dom = xml.dom.minidom.parseString(xml_string)
        return dom.toprettyxml()


def main():
    parser = argparse.ArgumentParser(description="Transform a custom config language to XML.")
    parser.add_argument("file", type=str, help="Path to the input file.")
    args = parser.parse_args()

    try:
        # Чтение файла
        with open(args.file, "r", encoding="utf-8") as file:
            content = file.readlines()

        # Парсинг
        parser = ConfigParser(content)
        parsed_data = parser.parse()

        # Преобразование в XML
        xml_output = ConfigToXML.convert(parsed_data)
        formatted_xml = ConfigToXML.format_xml(xml_output)

        # Запись в файл output.xml
        with open("output.xml", "w", encoding="utf-8") as output_file:
            output_file.write(formatted_xml)

        print("XML has been written to output.xml")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
