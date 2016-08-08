import markdown


class MathPattern(markdown.inlinepatterns.Pattern):
    def __init__(self):
        markdown.inlinepatterns.Pattern.__init__(self, r'(?<!\\)(\$\$?)(.+?)\2')

    def handleMatch(self, m):
        node = markdown.util.etree.Element('span class="math"')
        # node.text = markdown.util.AtomicString(m.group(2) + m.group(3) + m.group(2))
        if m.group(2) == "$$":
            node.text = markdown.util.AtomicString("\[" + m.group(3) + "\]")
        else:
            node.text = markdown.util.AtomicString("\(" + m.group(3) + "\)")
        return node


class MathExtension(markdown.Extension):

    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns.add('math', MathPattern(), '<escape')