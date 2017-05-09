from cms.models import Placeholder
from cms.plugin_rendering import ContentRenderer
from sekizai.context import SekizaiContext

import diff_match_patch as dmp


def revert_escape(txt, transform=True):
    """
    transform replaces the '<ins ' or '<del ' with '<div '
    :type transform: bool
    """
    html = txt.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&para;<br>", "\n")
    if transform:
        html = html.replace('<ins ', '<div ').replace('<del ', '<div ').replace('</ins>', '</div>')\
            .replace('</del>', '</div>')
    return html


def create_placeholder_contents(left_page, right_page, request, language):
    # persist rendered html content for each placeholder for later use in diff
    placeholders_a = Placeholder.objects.filter(page=left_page.pk).order_by('slot')
    placeholders_b = Placeholder.objects.filter(page=right_page.pk).order_by('slot')
    placeholders = zip(placeholders_a, placeholders_b)
    diffs = {}
    for p1, p2 in placeholders:
        body1 = placeholder_html(p1, request, language)
        body2 = placeholder_html(p2, request, language)
        diff = diff_texts(body2, body1)
        diffs[p1.slot] = {'left': revert_escape(body1), 'right': revert_escape(body2),
                          'diff_right_to_left': diff}
    return diffs


def placeholder_html(placeholder, request, language):
    if hasattr(placeholder, '_plugins_cache'):
        del placeholder._plugins_cache
    context = SekizaiContext({'request': request})
    renderer = ContentRenderer(request)
    return renderer.render_placeholder(placeholder, context, language=language).strip()


def diff_texts(text1, text2):
    differ = dmp.diff_match_patch()
    diffs = differ.diff_main(text1, text2)
    differ.diff_cleanupEfficiency(diffs)
    for i in range(len(diffs)):
        diffs[i] = [diffs[i][0], revert_escape(diffs[i][1])]
    return diffs


