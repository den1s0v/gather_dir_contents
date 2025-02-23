# Python
# 23.02.2025
# pip install fs
import os
import sys
import argparse
from fs import open_fs
from fs.walk import Walker
from fs.gitignore import GitIgnoreMatcher

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
    if use_gitignore and fs.exists('.gitignore'):
        with fs.open('.gitignore', 'r') as gitignore_file:
            ignore_patterns = gitignore_file.read().splitlines()
        ignore_matcher = GitIgnoreMatcher(ignore_patterns)

    # Рекурсивно обходим директорию
    walker = Walker(filter=['*.py', '*.txt', '*.md', '*.json', '*.yaml', '*.yml'])  # Фильтр по расширениям
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
    with open(output_path, 'w') as output_file:
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
