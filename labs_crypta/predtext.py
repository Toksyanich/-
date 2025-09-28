import docx

# Алфавит, который мы хотим оставить в тексте (из вашего задания)
ALLOWED_CHARACTERS = "abcdefghijklmnopqrstuvwxyz,.: "


def process_text(text):
    """
    Обрабатывает текст: переводит в нижний регистр и фильтрует символы.

    :param text: Исходная строка текста.
    :return: Обработанная строка.
    """
    # 1. Переводим весь текст в нижний регистр
    lower_text = text.lower()

    # 2. Создаем новую строку, добавляя только разрешенные символы
    filtered_text = ""
    for char in lower_text:
        if char in ALLOWED_CHARACTERS:
            filtered_text += char

    return filtered_text


def convert_docx_to_processed_txt(docx_path, txt_path):
    """
    Читает текст из .docx файла, обрабатывает его и сохраняет в .txt файл.

    :param docx_path: Путь к исходному .docx файлу.
    :param txt_path: Путь к целевому .txt файлу для сохранения результата.
    """
    try:
        # Открываем .docx файл
        doc = docx.Document(docx_path)

        # Считываем текст из всех параграфов документа
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)

        # Объединяем все параграфы в одну большую строку
        original_text = '\n'.join(full_text)

        # Обрабатываем текст
        cleaned_text = process_text(original_text)

        # Сохраняем обработанный текст в .txt файл
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_text)

        print(f"Файл успешно обработан и сохранен как '{txt_path}'")
        print(f"Исходное количество символов: {len(original_text)}")
        print(f"Количество символов после обработки: {len(cleaned_text)}")

    except FileNotFoundError:
        print(
            f"Ошибка: Файл '{docx_path}' не найден. Убедитесь, что он находится в той же папке, что и скрипт, или укажите полный путь.")
    except Exception as e:
        print(f"Произошла непредвиденная ошибка: {e}")


# --- ОСНОВНАЯ ЧАСТЬ ---
if __name__ == "__main__":
    # Укажите здесь имена ваших файлов
    input_docx_file = "nado.docx"  # Имя вашего Word файла
    output_txt_file = "test1.txt"     # Имя файла, который будет использоваться в лабе

    convert_docx_to_processed_txt(input_docx_file, output_txt_file)
