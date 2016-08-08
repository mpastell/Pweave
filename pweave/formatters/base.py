import textwrap

# Pweave output formatters
class PwebFormatter(object):
    """Base class for all formatters"""

    def __init__(self, source=None):
        self.initformat()
        self._fillformatdict()
        self.header = None
        self.footer = None
        self.executed = None
        self.source = source
        self.wrapper = textwrap.TextWrapper(subsequent_indent="", break_long_words=False)

    def setexecuted(self, executed):
        self.executed = executed

    def format(self):
        self.formatted = []
        for chunk in self.executed:
            # Fill in options for code chunks
            if chunk['type'] == "code":
                for key in self.formatdict.keys():
                    if not key in chunk:
                        chunk[key] = self.formatdict[key]

            # Wrap text if option is set
            if chunk['type'] == "code":
                if chunk['wrap']:
                    chunk['content'] = self._wrap(chunk['content'])
                    chunk['result'] = self._wrap(chunk['result'])
                if chunk['wrap'] == 'code':
                    chunk['content'] = self._wrap(chunk['content'])
                if chunk['wrap'] == 'results':
                    chunk['result'] = self._wrap(chunk['result'])
                if not chunk['wrap']:
                    chunk['content'] = chunk['content'] + "\n"

            # Preformat chunk content before default formatters
            chunk = self.preformat_chunk(chunk)

            if chunk['type'] == "doc":
                self.formatted.append(self.format_docchunk(chunk))
            elif chunk['type'] == "code":
                self.formatted.append(self.format_codechunks(chunk))
            else:
                self.formatted.append(chunk["content"])

        self.formatted = "\n".join(self.formatted)
        self.convert()  # Convert to e.g. markdown
        self.add_header()
        self.add_footer()

    def convert(self):
        pass

    def preformat_chunk(self, chunk):
        """You can use this method in subclasses to preformat chunk content"""
        return chunk

    def format_termchunk(self, chunk):
        if chunk['echo'] and chunk['results'] != 'hidden':
            chunk['result'] = self._termindent(chunk['result'])
            result = '%(termstart)s%(result)s%(termend)s' % chunk
        else:
            result = ""
        return result

    def format_codeblock(self, chunk):
        pass

    def format_results(self, chunk):
        pass

    def format_codechunks(self, chunk):
        chunk['content'] = self._indent(chunk['content'])

        # Code is not executed
        if not chunk['evaluate']:
            if "%s" in chunk["codestart"]:
                chunk["codestart"] = chunk["codestart"] % chunk["engine"]
            if chunk['echo']:
                result = '%(codestart)s%(content)s%(codeend)s' % chunk
                return result
            else:
                return ''

        #Set lexers for code and output
        if "%s" in chunk["codestart"]:
            chunk["codestart"] = chunk["codestart"] % chunk["engine"]
        if "%s" in chunk["outputstart"]:
            chunk["outputstart"] = chunk["outputstart"] % chunk["engine"]
        if "%s" in chunk["termstart"]:
            chunk["termstart"] = chunk["termstart"] % chunk["engine"]

        #Code is executed
        #-------------------
        result = ""

        #Hidden results
        if chunk['results'] == 'hidden':
            chunk['result'] = ''

        #Term sets echo to true
        if chunk['term']:
            result = self.format_termchunk(chunk)
        #Other things than term
        elif chunk['evaluate'] and chunk['echo'] and chunk['results'] == 'verbatim':
            result = '%(codestart)s%(content)s%(codeend)s' % chunk
            if len(chunk['result'].strip()) > 1:
                chunk['result'] = self._indent(chunk['result'])
                result += '%(outputstart)s%(result)s%(outputend)s' % chunk

        elif chunk['evaluate'] and chunk['echo'] and chunk['results'] != 'verbatim':
            chunk['result'] = chunk['result'].replace('\n', '', 1)
            result = '%(codestart)s%(content)s%(codeend)s%(result)s' % chunk

        elif chunk['evaluate'] and not chunk['echo'] and chunk['results'] == 'verbatim':
            if len(chunk['result'].strip()) > 1:
                chunk['result'] = self._indent(chunk['result'])
                result += '%(outputstart)s%(result)s%(outputend)s' % chunk

        elif chunk['evaluate'] and not chunk['echo']:
            #Remove extra line added when results are captured in run phase
            result = chunk['result'].replace('\n', '', 1)

        #Handle figures
        if chunk['fig'] and 'figure' in chunk:
            if chunk['include']:
                result += self.formatfigure(chunk)
        return result

    def format_docchunk(self, chunk):
        return chunk['content']

    def add_header(self):
        """Can be used to add header to self.formatted list"""
        if self.header is not None:
            self.formatted = self.header + self.formatted

    def add_footer(self):
        """Can be used to add footer to self.formatted list"""
        if self.footer is not None:
            self.formatted += self.footer

    def getformatdict(self):
        return self.formatdict

    def getformatted(self):
        return self.formatted

    def updateformatdict(self, format_dict):
        self.formatdict.update(format_dict)

    def _wrapper(self, string, width=80):
        """Wrap a string to specified width like Python terminal"""
        if len(string) < width:
            return string
        # Wrap also comment lines
        if string.lstrip()[0] == "#":
            return string[0:width] + '\n' + self._wrapper("#" + string[width:len(string)], width)
        else:
            return string[0:width] + '\n' + self._wrapper(string[width:len(string)], width)

    def _wrap(self, content):
        splitted = content.split("\n")
        result = ""
        for line in splitted:
            result += self.wrapper.fill(line) + '\n'
        return result

    def _fillformatdict(self):
        """Fill in the blank options that are now only used for rst
            but also allow e.g. special latex style for terminal blocks etc."""
        self._fillkey('termstart', self.formatdict['codestart'])
        self._fillkey('termend', self.formatdict['codeend'])
        self._fillkey('savedformats', list([self.formatdict['figfmt']]))

    def _fillkey(self, key, value):
        if key not in self.formatdict:
            self.formatdict[key] = value

    def _indent(self, text):
        """Indent blocks for formats where indent is significant"""
        return text
        # return(text.replace('\n', '\n' + self.formatdict['indent']))

    def _termindent(self, text):
        """Indent blocks for formats where indent is significant"""
        return text
        # return(text.replace('\n', '\n' + self.formatdict['termindent']))
