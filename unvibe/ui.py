import json
import os
import sys
from bigtree import Node, print_tree, tree_to_dot

from unvibe import project_name
from unvibe.core import State


def create_page_and_open_browser(root):
    page_file = create_html_page(root)
    if sys.platform == 'darwin':
        os.system(f'open {page_file}')
    elif sys.platform == 'win32':
        os.system(f'start {page_file}')
    elif sys.platform == 'linux':
        os.system(f'xdg-open {page_file}')
    return page_file


def create_html_page(root):
    template_path = os.path.join(os.path.dirname(__file__), 'ui.html')
    with open(template_path, 'r') as f:
        template = f.read()
    tree_html = build_html_tree(root)
    try:
        img_file = save_bigtree_img(root)
        template = template.replace('__TREE_IMG__', img_file)
    except Exception as exc:
        pass
    template = template.replace('__TREE__', tree_html)
    template = template.replace('__JSON_TREE__', json.dumps(root.to_dict()))
    func_names = '_'.join([mf.name for mf in root.mes])
    report_file = f'{project_name}_report_{func_names}.html'  # Use the same file for each run
    with open(report_file, 'w') as f:
        f.write(template)
    return report_file


def build_html_tree(root):
    html = '<ul>'
    for child in root.children:
        html += f'<li><span class="node" id="{child.count}">{str(child)}</span>'
        if child.children:
            html += build_html_tree(child)
        html += '</li>'
    html += '</ul>'
    return html


def make_bigtree(node: State, is_root=True):
    if is_root:
        name = ','.join([mf.name for mf in node.mes])
    else:
        name = node.short_repr()
    bt = Node(name)
    for child in node.children:
        bt >> make_bigtree(child, is_root=False)
    return bt


def save_bigtree_img(root: State):
    bt = make_bigtree(root)
    func_names = ','.join([mf.name for mf in root.mes])
    print_tree(bt)
    graph = tree_to_dot(bt, node_colour="gold")
    file_name = f"unvibe_tree_{func_names}.png"
    graph.write_png(file_name)
    return file_name