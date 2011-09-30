

#Format chunks
#def formatdocchunk(chunk):
#    return(chunk['content'])

#A test formatter for custom call code
#def formatcapschunk(chunk):
#    return(chunk['content'].upper())

#Format figures
def addtexfigure(chunk):
    figname = chunk['figure']
    caption = chunk['caption']
    width = chunk['width']
    result = ""   

    if chunk['caption']:
        result += ("\\begin{figure}\n"\
                    "\\includegraphics[width= %s]{%s}\n"\
                    "\\caption{%s}\n"\
                    "\end{figure}\n" % (width, figname, caption))
    else:
        result += "\\includegraphics[width=%s]{%s}\n" % (width, figname)
    return(result)


def addrstfigure(chunk):
    figname = chunk['figure']
    caption = chunk['caption']
    width = chunk['width']
    result = ""   

    if chunk['caption']:
        result += (".. figure:: %s\n"\
                    "   :width: %s\n\n"\
                    "   %s\n\n" % (figname, width, caption))
    else:
        result += ('.. image:: %s\n   :width: %s\n\n'   % (figname, width))
    return(result)
     
def addpandocfigure(chunk):
    figname = chunk['figure']
    caption = chunk['caption']
    width = chunk['width']
    result = ""   
        
    if chunk['caption']:
        result += '![%s](%s)\n' % (caption, figname)
    else:
        result += '![](%s)\\\n' % (figname)
    return(result)

def addsphinxfigure(chunk):
    figname = chunk['figure']
    caption = chunk['caption']
    width = chunk['width']
    result = ""   

    if chunk['caption']:
        result += (".. figure:: %s\n"\
                    "   :width: %s\n\n"\
                    "   %s\n\n" % (figname, width, caption))
    else:
        result += ('.. image:: %s\n   :width: %s\n\n'   % (figname, width))
    return(result)

