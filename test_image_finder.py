import markdown
from image_finder import ImageFinder

def test_image_finder():
    md = markdown.markdown('\n![](image)\n', extensions=[ImageFinder()])

    print(md)


