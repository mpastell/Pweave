from IPython.core.display import display_html
import hashlib

display_html(
    """
<script src="https://cdn.jsdelivr.net/npm/vega@3"></script>
<script src="https://cdn.jsdelivr.net/npm/vega-lite@2"></script>
<script src="https://cdn.jsdelivr.net/npm/vega-embed@3"></script>
""",
    raw=True)


def show(plot):
    """
    Include an Altair (vega) figure in Pweave document.
    Generates html output.
    """
    json = plot.to_json()
    id = "A" + hashlib.sha256(json.encode()).hexdigest()
    display_html(
        """
 <div id="{id}"></div>
  <script type="text/javascript">
    var spec = {json};
    var opt = {{"renderer": "canvas", "actions": false}};
    vegaEmbed("#{id}", spec, opt);
  </script>
  """.format(id=id, json=json),
        raw=True)
