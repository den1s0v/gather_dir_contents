# `generate_directory_contents.py` can prepare a `directory_contents.txt` file with the contents of the directory files from the folder at the specified path (cmd argument)
Optionally, the `.gitignore` file may be taken into account if it exists in the specified directory (flag -i, --gitignore).

### Installing dependencies
```bash
pip install fs
```


### Usage
1. **Run ignoring `.gitignore`**:
   ```bash
   python generate_directory_contents.py /path/to/your/directory
   ```

2. **Run using `.gitignore`**:
   ```bash
   python generate_directory_contents.py /path/to/your/directory --gitignore
   ```

---

### Output example
If `.gitignore` contains:
```gitignore
/build/
*.log
```

And the structure of the project:
```
/project
  /src
    main.py
    utils.py
  /build
    built.py
  temp.log
  .gitignore
```

Then the `directory_contents.txt` file will contain the following:
```
===== /src/main.py (7 lines) =====
import utils

def main():
    print("Hello, world!")

if __name__ == "__main__":
    main()
===== End of /src/main.py =====

===== /src/utils.py (2 lines) =====
def helper():
    return "This is a helper function."
===== End of /src/utils.py =====
```

#### Notes

Thanks to DeepSeek for the code generation, thanks to me for the idea generation ☺.
The conversation can be found in `about.md`.
