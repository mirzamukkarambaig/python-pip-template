# python-pip-template

A lightweight Python project template designed to simplify dependency management and environment setup using `pip`.

---

## 🚀 Overview

This template provides a clean structure for Python applications using `pip` and `pyproject.toml`. It supports multiple environments: development, testing, and production.

---

## ✅ Prerequisites

Make sure you have the following before getting started:

- [Python 3.x](https://www.python.org/downloads/)
- A terminal or command prompt

---

## ⚙️ Local Setup

Install the project dependencies based on your desired environment:

### Development
```bash
pip install -e ".[dev]"
```

### Testing
```bash
pip install -e ".[test]"
```

### Production
```bash
pip install -e ".[prod]"
```

---

## 🐳 Docker Setup

Build the Docker image for the appropriate environment:

### Development
```bash
docker build --build-arg ENVIORNMENT=dev -t <your_tag> .
```

### Testing
```bash
docker build --build-arg ENVIORNMENT=test -t my-app .
```

### Production
```bash
docker build --build-arg ENVIORNMENT=prod -t my-app .
```

---

## 🛠️ Additional Notes

- **Managing Dependencies:** Edit your `pyproject.toml` file to update dependencies as needed.

---

## 🤝 Contributing

Contributions are welcome! Feel free to fork this repo and open a pull request with improvements, fixes, or suggestions.

---

## 📄 License

This project is licensed under the [Apache-2.0 License](LICENSE).
