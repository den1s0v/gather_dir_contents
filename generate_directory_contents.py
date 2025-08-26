# Python
# Since 23.02.2025
# pip install fs
import os
import sys
import argparse
import fnmatch
from fs import open_fs
from fs.walk import Walker


# Фильтр по расширениям файлов, которые будут использованы
EXTENSIONS = [
    '*.py',
    '*.java',
    # '*.txt',  # игнорировать сам файл directory_contents.txt, если он есть
    '*.md', '*.json', '*.yaml', '*.yml',
    '*.php',
]

IGNORE_FILE_PATTERNS = [
    'LICENSE',
    'LICENSE.*',
]


class GitIgnoreMatcher:
    def __init__(self, gitignore_path, ignore_custom=IGNORE_FILE_PATTERNS):
        """Инициализирует matcher на основе файла .gitignore."""
        self.patterns = []
        if os.path.exists(gitignore_path):
            with open(gitignore_path, 'r', encoding='utf-8') as gitignore_file:
                self.patterns = [
                    line.strip() for line in gitignore_file
                    if line.strip() and not line.startswith("#")
                ]
        if ignore_custom:
            self.patterns += ignore_custom

    def match(self, path):
        """Проверяет, соответствует ли путь какому-либо правилу из .gitignore."""
        for pattern in self.patterns:
            # Игнорируем директории, если паттерн заканчивается на /
            if pattern.endswith('/'):
                if fnmatch.fnmatch(path, pattern[:-1]) or fnmatch.fnmatch(path, pattern + "*"):
                    return True
            else:
                if fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(os.path.basename(path), pattern):
                    return True
        return False

def read_file_content(file_path):
    """Читает содержимое файла и возвращает его как строку."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def get_common_parent(paths):
    """Находит общий родительский каталог для списка путей."""
    if not paths:
        return None

    common_prefix = os.path.commonprefix([
    	os.path.dirname(os.path.abspath(p))
    	for p in paths
	])
    if os.path.isdir(common_prefix):
        return common_prefix
    else:
        return os.path.dirname(common_prefix)

def process_single_item(item_path, common_parent, ignore_matcher=None):
    """Обрабатывает один файл или директорию."""
    output_lines = []

    if os.path.isfile(item_path):
        # Обработка файла
        relative_path = os.path.relpath(item_path, common_parent)

        # Проверка на игнорирование
        if ignore_matcher and ignore_matcher.match(relative_path):
            print(f"Ignoring: {relative_path}")
            return

        # Проверка расширения файла
        ext_matched = any(fnmatch.fnmatch(item_path.lower(), '*' + ext.lower()) for ext in EXTENSIONS)
        if not ext_matched:
            return

        try:
            content = read_file_content(item_path)
            line_count = len(content.splitlines())
            output_lines.append(f"===== {relative_path} ({line_count} lines) =====")
            output_lines.append(content)
            output_lines.append(f"===== End of {relative_path} =====\n")
        except Exception as e:
            print(f"Error reading {item_path}: {e}")

    elif os.path.isdir(item_path):
        # Обработка директории
        fs = open_fs(item_path)
        walker = Walker(filter=EXTENSIONS)

        for path in walker.files(fs):
            # full_path = os.path.join(item_path, path)
            full_path = fs.getsyspath(path)
            relative_path = os.path.relpath(full_path, common_parent)

            # Проверка на игнорирование
            if ignore_matcher and ignore_matcher.match(relative_path):
                print(f"Ignoring: {relative_path}")
                continue

            try:
                content = read_file_content(full_path)
                line_count = len(content.splitlines())
                output_lines.append(f"===== {relative_path} ({line_count} lines) =====")
                output_lines.append(content)
                output_lines.append(f"===== End of {relative_path} =====\n")
            except Exception as e:
                print(f"Error reading {full_path}: {e}")
    else:
        print(f"Undetermined type of path: {full_path}")

    return output_lines

def generate_contents(paths, use_gitignore, output_filename):
    """Переписвает содержимое файлов и директорий в текстовый файл."""
    # report
    print("Processing paths:", *paths, sep='\n  ')

    output_lines = []

    # Находим общий родительский каталог
    common_parent = get_common_parent(paths)
    if not common_parent:
        print("Error: No valid paths provided.")
        return

    # Создаём matcher для .gitignore, если нужно
    ignore_matcher = None
    if use_gitignore:
        gitignore_path = os.path.join(common_parent, '.gitignore')
        ignore_matcher = GitIgnoreMatcher(gitignore_path)

    # Обрабатываем каждый путь
    for path in paths:
        item_lines = process_single_item(path, common_parent, ignore_matcher)
        if item_lines:
	        output_lines += item_lines
        else:
        	print('Empty object:', path)

    # Сохраняем результат
    output_path = os.path.join(common_parent, output_filename)
    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.write("\n".join(output_lines))

    print(f"Contents saved to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Generate a contents file from multiple files/directories.")
    parser.add_argument("paths", nargs="+", help="Paths to files and/or directories")
    parser.add_argument("-i", "--gitignore", action="store_true", help="Respect .gitignore file")
    args = parser.parse_args()

    # Проверяем, что все пути существуют
    valid_paths = []
    for path in args.paths:
        if os.path.exists(path):
            valid_paths.append(path)
        else:
            print(f"Warning: Path '{path}' does not exist, skipping.")

    if not valid_paths:
        print("Error: No valid paths provided.")
        sys.exit(1)

    # Определяем имя выходного файла
    if len(valid_paths) == 1 and os.path.isdir(valid_paths[0]):
        output_filename = "directory_contents.txt"
    else:
        output_filename = "files_contents.txt"

    generate_contents(valid_paths, args.gitignore, output_filename)

if __name__ == "__main__":
    main()
