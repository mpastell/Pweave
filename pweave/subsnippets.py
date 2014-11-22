#Code snippets that are executed by subprocess writer

savefigs = """
import os
import json
chunk = __pweave_data__["chunk"]
rcParams = __pweave_data__["rcParams"]
prefix = __pweave_data__["prefix"]
formatdict = __pweave_data__["formatdict"]
cwd = __pweave_data__["cwd"]

figs = plt.get_fignums()
fignames = []
for i in figs:
    plt.figure(i)
    plt.figure(i).set_size_inches(chunk['f_size'])
    if not chunk["f_spines"]:
        axes = plt.figure(i).axes
        for ax in axes:
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
            ax.yaxis.set_ticks_position('left')
            ax.xaxis.set_ticks_position('bottom')
    name = rcParams["figdir"] + "/" + prefix + "_" + str(i) + formatdict['figfmt']
    for format in formatdict['savedformats']:
        f_name = os.path.join(cwd, rcParams["figdir"], prefix + "_" + str(i)) + format
        plt.savefig(f_name)
        plt.draw()
    fignames.append(name)
    plt.close()



if len(fignames):
    print('<chunkfigs id="figs%s">%s</chunkfigs>' % (chunk["number"], json.dumps(fignames)))
"""


savefigs_winston = """
_pweave_figs = copy(Winston._display.fig_order)
for i =_pweave_figs
    figure(i)
    savefig(%s)
    closefig(i)
end
"""