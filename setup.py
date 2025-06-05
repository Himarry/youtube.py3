from setuptools import setup, find_packages
import sys
import os

# READMEファイルの読み込み（存在しない場合のエラーハンドリング）
long_description = ""
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "A simplified wrapper for YouTube Data API v3"

# バージョン情報を動的に取得
def get_version():
    version_file = os.path.join("youtube_py2", "__init__.py")
    if os.path.exists(version_file):
        with open(version_file, "r", encoding="utf-8") as f:
            content = f.read()
            for line in content.split('\n'):
                if line.startswith('__version__'):
                    return line.split('"')[1]
    return "1.0.0"

# コマンドライン引数がない場合のデフォルト動作
if len(sys.argv) == 1:
    print("YouTube.py2 - Setup Script")
    print("=" * 50)
    print("使用可能なコマンド:")
    print("  python setup.py build       - パッケージをビルド")
    print("  python setup.py install     - パッケージをインストール")
    print("  python setup.py sdist       - ソース配布を作成")
    print("  python setup.py bdist_wheel - Wheelパッケージを作成")
    print("  python setup.py develop     - 開発モードでインストール")
    print("  python setup.py clean       - ビルドファイルを削除")
    print("  python setup.py --help      - ヘルプを表示")
    print()
    print("推奨:")
    print("  pip install -e .            - 開発モードでインストール")
    print("  pip install .               - 通常インストール")
    sys.exit(0)

setup(
    name="youtube-py2",
    version=get_version(),
    author="Chihalu",
    author_email="m.chihiro0314@gmail.com",
    description="A simplified wrapper for YouTube Data API v3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Himarry/youtube.py2",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.7",
    install_requires=[
        "google-api-python-client>=2.0.0",
        "google-auth>=2.0.0",
        "google-auth-oauthlib>=0.5.0",
        "google-auth-httplib2>=0.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.910",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    keywords="youtube api wrapper python google data v3",
    project_urls={
        "Bug Reports": "https://github.com/Himarry/youtube.py2/issues",
        "Source": "https://github.com/Himarry/youtube.py2",
        "Documentation": "https://github.com/Himarry/youtube.py2#readme",
    },
    include_package_data=True,
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "youtube-py2=youtube_py2.cli:main",
        ],
    },
)
