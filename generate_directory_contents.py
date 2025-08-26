# Python
# 23.02.2025
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
            with open(gitignore_path, 'r') as gitignore_file:
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

def read_file_content(fs, path):
    """Читает содержимое файла и возвращает его как строку."""
    with fs.open(path, 'r') as file:
        return file.read()

def generate_directory_contents(directory_path, use_gitignore):
    """Генерирует содержимое директории в виде текстового файла."""
    output_lines = []
    fs = open_fs(directory_path)

    # Если используется .gitignore, создаём matcher
    ignore_matcher = None
    if use_gitignore:
        gitignore_path = os.path.join(directory_path, '.gitignore')
        ignore_matcher = GitIgnoreMatcher(gitignore_path)

    # Рекурсивно обходим директорию
    walker = Walker(filter=EXTENSIONS)  # Фильтр по расширениям
    for path in walker.files(fs):
        # Пропускаем файлы, если они соответствуют .gitignore
        if ignore_matcher and ignore_matcher.match(path):
            print(f"Ignoring: {path}")
            continue

        # Читаем содержимое файла
        try:
            content = read_file_content(fs, path)
            line_count = len(content.splitlines())
            # Добавляем разделитель и содержимое файла
            output_lines.append(f"===== {path} ({line_count} lines) =====")
            output_lines.append(content)
            output_lines.append(f"===== End of {path} =====\n")
        except Exception as e:
            print(f"Error reading {path}: {e}")

    # Сохраняем результат в файл
    output_path = os.path.join(directory_path, 'directory_contents.txt')
    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.write("\n".join(output_lines))

    print(f"Directory contents saved to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Generate a directory contents file.")
    parser.add_argument("directory", help="Path to the directory")
    parser.add_argument("-i", "--gitignore", action="store_true", help="Respect .gitignore file")
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"Error: {args.directory} is not a valid directory.")
        sys.exit(1)

    generate_directory_contents(args.directory, args.gitignore)

if __name__ == "__main__":
    main()
