def create_page(root):
    with open('tree.html', 'w') as f:
        template = f.read()
    tree_html = build_tree(root)
    template.replace('__TREE__', tree_html)


def build_tree(root):
    html = '<ul>'
    for child in root.children:
        html += '<li>' + child.data
        if child.children:
            html += build_tree(child)
        html += '</li>'
    html += '</ul>'
    return html
