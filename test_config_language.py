from config_language import ConfigParser, ConfigToXML
import xml.etree.ElementTree as ET


def parse_config(config_text):
    """Функция для парсинга конфигурации и преобразования в XML."""
    content = config_text.strip().splitlines()
    parser = ConfigParser(content)
    parsed_data = parser.parse()
    xml_output = ConfigToXML.convert(parsed_data)
    return ET.fromstring(xml_output)


def test_application_settings():
    """Тест: Настройки приложения."""
    config_text = """
    base_font_size := 14;
    default_theme := [[light]];
    user_settings := {
        appearance => {
            theme => [[dark]],
            font => {
                size => |base_font_size|,
                family => [[Arial]],
            },
        },
        notifications => {
            email => [[enabled]],
            sms => [[disabled]],
        },
        version => 1,
    };
    """
    xml_tree = parse_config(config_text)

    # Проверяем базовые константы
    assert xml_tree.find(".//constant[@name='base_font_size']").text == "14"
    assert xml_tree.find(".//constant[@name='default_theme']").text == "light"

    # Проверяем вложенные словари
    appearance = xml_tree.find(".//constant[@name='user_settings']//entry[@key='appearance']")
    assert appearance is not None
    assert appearance.find(".//entry[@key='theme']").text == "dark"

    # Проверяем константу в словаре
    font_size = appearance.find(".//entry[@key='font']//entry[@key='size']")
    assert font_size.text == "14"

    print("test_application_settings passed!")


def test_car_specifications():
    """Тест: Параметры автомобиля."""
    config_text = """
    base_speed := 120;
    car_specifications := {
        engine => {
            type => [[V8]],
            power => [[450 HP]],
        },
        dimensions => {
            length => [[4.5 m]],
            width => [[1.8 m]],
            height => [[1.4 m]],
        },
        performance => {
            top_speed => |base_speed|,
            acceleration => [[3.8 s to 100 km/h]],
        },
        features => {
            safety => [[Airbags, ABS, ESP]],
            comfort => [[Climate control, Leather seats]],
        },
    };
    """
    xml_tree = parse_config(config_text)

    # Проверяем базовую скорость
    assert xml_tree.find(".//constant[@name='base_speed']").text == "120"

    # Проверяем вложенные параметры
    engine = xml_tree.find(".//constant[@name='car_specifications']//entry[@key='engine']")
    assert engine is not None
    assert engine.find(".//entry[@key='type']").text == "V8"
    assert engine.find(".//entry[@key='power']").text == "450 HP"

    # Проверяем вложенные характеристики
    performance = xml_tree.find(".//entry[@key='performance']")
    assert performance.find(".//entry[@key='top_speed']").text == "120"
    assert performance.find(".//entry[@key='acceleration']").text == "3.8 s to 100 km/h"

    print("test_car_specifications passed!")


def test_nested_dictionaries():
    """Тест: Сложная вложенность словарей."""
    config_text = """
    root := {
        level1 => {
            level2 => {
                level3 => {
                    value => [[deep]],
                },
            },
        },
        flat_value => [[shallow]],
    };
    """
    xml_tree = parse_config(config_text)

    # Проверяем вложенные уровни
    level3 = xml_tree.find(".//constant[@name='root']//entry[@key='level1']//entry[@key='level2']//entry[@key='level3']")
    assert level3 is not None
    assert level3.find(".//entry[@key='value']").text == "deep"

    # Проверяем верхний уровень
    flat_value = xml_tree.find(".//constant[@name='root']//entry[@key='flat_value']")
    assert flat_value.text == "shallow"

    print("test_nested_dictionaries passed!")


def test_constant_evaluation():
    """Тест: Объявление и использование констант."""
    config_text = """
    constant_value := 42;
    evaluated_value := |constant_value|;
    settings := {
        key => |constant_value|,
    };
    """
    xml_tree = parse_config(config_text)

    # Проверяем объявление и использование констант
    constant = xml_tree.find(".//constant[@name='constant_value']")
    assert constant.text == "42"

    evaluated = xml_tree.find(".//constant[@name='evaluated_value']")
    assert evaluated.text == "42"

    # Проверяем использование константы в словаре
    key_value = xml_tree.find(".//constant[@name='settings']//entry[@key='key']")
    assert key_value.text == "42"

    print("test_constant_evaluation passed!")


if __name__ == "__main__":
    try:
        print("Running test_application_settings...")
        test_application_settings()

        print("\nRunning test_car_specifications...")
        test_car_specifications()

        print("\nRunning test_nested_dictionaries...")
        test_nested_dictionaries()

        print("\nRunning test_constant_evaluation...")
        test_constant_evaluation()

        print("\nAll tests passed!")
    except AssertionError as e:
        print("Test failed:", e)
