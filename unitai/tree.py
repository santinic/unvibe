import json
import os
import sys
import time


def create_page_and_open_browser(root):
    page_file = create_page(root)
    if sys.platform == 'darwin':
        os.system(f'open {page_file}')
    elif sys.platform == 'win32':
        os.system(f'start {page_file}')
    elif sys.platform == 'linux':
        os.system(f'xdg-open {page_file}')


def create_page(root):
    template_path = os.path.join(os.path.dirname(__file__), 'tree.html')
    with open(template_path, 'r') as f:
        template = f.read()
    tree_html = build_tree(root)
    template = template.replace('__TREE__', tree_html)
    template = template.replace('__JSON_TREE__', json.dumps(root.to_dict()))
    timestamp = str(int(time.time())).replace('.', '')
    report_file = f'tree_{timestamp}.html'
    print(report_file)
    with open(report_file, 'w') as f:
        f.write(template)
    return report_file


def build_tree(root):
    html = '<ul>'
    for child in root.children:
        html += '<li>' + str(child)
        if child.children:
            html += build_tree(child)
        html += '</li>'
    html += '</ul>'
    return html
