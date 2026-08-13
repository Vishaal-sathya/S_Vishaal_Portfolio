import re
import os

with open('Implementing a GPT model part 1.md', 'r', encoding='utf-8') as f:
    md = f.read()

# Strip frontmatter
md = re.sub(r'^---\n.*?\n---\n', '', md, flags=re.DOTALL)

# Replace ![[img]] \n *caption* with the HTML structure
def replace_img(match):
    img = match.group(1)
    caption = match.group(2)
    return f'''<div class=\"blog-image-wrapper\">
            <img class=\"blog-image\" src=\"../images/blogs/implementing-a-gpt-model-part-1/{img}\" alt=\"{caption}\" />
            <p class=\"blog-image-caption\">{caption}</p>
          </div>'''

md = re.sub(r'!\[\[(.*?)\]\]\n\*(.*?)\*', replace_img, md)

# Key Takeaways
def replace_takeaways(match):
    items_text = match.group(1)
    items = re.findall(r'> - (.*)', items_text)
    li_elements = ''.join([f'<li>{item}</li>\n' for item in items])
    return f'''<div class=\"takeaways-box\">
            <h4>Key Takeaways</h4>
            <ul>
{li_elements}            </ul>
          </div>'''

md = re.sub(r'> \*\*Key Takeaways\*\*\n((?:> - .*\n?)+)', replace_takeaways, md)

# Note block
def replace_note(match):
    title = match.group(1)
    text = match.group(2)
    return f'''<div class=\"takeaways-box\">
            <h4>{title}</h4>
            <p>{text}</p>
          </div>'''

md = re.sub(r'> \*\*(.*?)\*\*\n> (.*)', replace_note, md)

# Now convert the rest to HTML using markdown library
import markdown
html_content = markdown.markdown(md, extensions=['fenced_code', 'tables'])

# Read the template
with open('blogs/coding-attention-mechanisms-part-4.html', 'r', encoding='utf-8') as f:
    template = f.read()

# Replace Title
template = re.sub(r'<title>.*?</title>', '<title>Implementing a GPT Model Part 1: Architecture and Layer Normalization - Vishaal S Blog</title>', template)
template = re.sub(r'<h1.*?>.*?</h1>', '<h1>Implementing a GPT Model Part 1: Architecture and Layer Normalization</h1>', template)
template = re.sub(r'<h2 class=\"sidebar-title\">.*?</h2>', '<h2 class=\"sidebar-title\">\n          Implementing a GPT Model Part 1: Architecture and Layer Normalization\n        </h2>', template, flags=re.DOTALL)

# Replace Meta
template = re.sub(r'<span class=\"metadata-value\">2026\.07\.22</span>', '<span class=\"metadata-value\">2026.08.13</span>', template)
template = re.sub(r'7 Min Read', '8 Min Read', template)

# Replace the article body
# We find <article class="article-body"> ... </article>
article_start = template.find('<article class=\"article-body\">') + len('<article class=\"article-body\">')
article_end = template.find('</article>', article_start)

new_template = template[:article_start] + '\n' + html_content + '\n        ' + template[article_end:]

with open('blogs/implementing-a-gpt-model-part-1.html', 'w', encoding='utf-8') as f:
    f.write(new_template)

print('Conversion complete')
