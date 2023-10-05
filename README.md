# Zone-routing-protocol
Python implementation for Zone Routing Protocol for satellite network

# Set up File Path in the Python project

Follow these steps to set up flexible file paths in your Python project, allowing for easy collaboration and customization.

## 1. Use Relative Paths

Update your code to use relative paths for accessing the file within your project directory:
```python
# Use a relative path
file_path = 'data/filename.txt'
```

## 2. Use Environment Variables for Configurations
```python
import os

# Define the environment variable to hold the file path
FILE_PATH = os.environ.get('MY_PROJECT_FILE_PATH', 'data/filename.txt')

# Use FILE_PATH in your code to read the file
with open(FILE_PATH, 'r') as file:
    content = file.read()
```

## 3. Set the Environment Variable
Terminal (temporary setting):
```bash
export MY_PROJECT_FILE_PATH=/path/to/your/file/filename.txt
```

Environment Configuration File (e.g., .env): Create a '.env' file in your project's root folder, and add the file configuration as below.
```plaintext
MY_PROJECT_FILE_PATH=/path/to/your/file/filename.txt
```

## 4. Add .env to .gitignore
Ensure that the .env file is added to your .gitignore to prevent it from being pushed to the Git repository. This keeps the file path configurations local to each developer's environment. Add the following line to your .gitignore file:
file configuration as below.
```plaintext
.env
```


