import re
import bs4.element


def tag_has_attribute(tag: bs4.element.Tag, attribute_name:str) -> bool:
    return tag and tag.has_attr(attribute_name)


def is_aligned(align, alignment:str) -> bool:
    return align and re.compile(alignment, re.IGNORECASE).search(align)


def has_only_child_with_attribute(tag: bs4.element.Tag, child_name:str, attribute_name:str) -> bool:
    children = tag.find_all(child_name)
    if len(children) != 1:
        return False
    return children[0].has_attr(attribute_name)
