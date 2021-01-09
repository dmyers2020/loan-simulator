# Example Package

This is a simple example package. You can use
[Github-flavored Markdown](https://guides.github.com/features/mastering-markdown/)
to write your content.

WHEN GENERATING DISTRIBUTION ARCHIVES  MAKE SURE YOU HAVE THE LATEST VERSIONS OF SETUPTOOLS AND WHEEL INSTALLED:

python3-m pip install --user --upgrade setuptools wheel

THEN RUN THIS COMMAND FROM THE SAME DIRECTORY WHERE SETUPPY IS LOCATED

python setup.py sdist bdist_wheel

THIS COMMAND WILL OUTPUT A LOT OF TEXT AND ONCE COMPLETED SHOULD GERNEATE TWO FILES IN THE DIST DIRECTORY

dist/
  example_pkg_YOUR_USERNAME_HERE-0.0.1-py3-none-any.whl
  example_pkg_YOUR_USERNAME_HERE-0.0.1.tar.gz




