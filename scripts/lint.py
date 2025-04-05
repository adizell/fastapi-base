# scripts/lint.py

# Execute usando o script abaixo
# poetry run python scripts/lint.py

import subprocess
import os

# Caminho absoluto para o diretório "app"
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
APP_DIR = os.path.join(BASE_DIR, "app")


def main():
    print("🧹 Limpando código com autoflake...")
    subprocess.run(
        f"autoflake --in-place --remove-unused-variables --remove-all-unused-imports -r {APP_DIR}",
        shell=True,
    )

    print("📦 Organizando imports com isort...")
    subprocess.run(f"isort {APP_DIR}", shell=True)

    print("🖤 Formatando código com black...")
    subprocess.run(f"black {APP_DIR}", shell=True)

    print("🔍 Analisando com pylint...")
    subprocess.run(f"pylint {APP_DIR}", shell=True)

    print("✅ Finalizado com sucesso!")


if __name__ == "__main__":
    main()
