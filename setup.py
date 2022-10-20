from setuptools import setup
setup(
    name='image_finder',
    version='1.0',
    py_modules=['image_finder'],
    install_requires = ['markdown>=3.0'],
    entry_points = {
        'markdown.extensions':
        ['image_finder=image_finder:ImageFinder']
        }
)
