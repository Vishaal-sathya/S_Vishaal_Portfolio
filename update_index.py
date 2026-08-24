import re
import os

blog_list = [
    ("implementing-a-gpt-model-part-2.html", "Implementing a GPT Model Part 2: Feed Forward Networks and Transformer Blocks"),
    ("implementing-a-gpt-model-part-3.html", "Implementing a GPT Model Part 3: Generating Text"),
    ("pretraining-on-unlabeled-data-part-1.html", "Pretraining on Unlabeled Data Part 1: Creating a Data Loader"),
    ("pretraining-on-unlabeled-data-part-2.html", "Pretraining on Unlabeled Data Part 2: Training Loop and Loss"),
    ("pretraining-on-unlabeled-data-part-3.html", "Pretraining on Unlabeled Data Part 3: Loading Pretrained Weights"),
    ("fine-tuning-for-classification-1.html", "Fine-Tuning for Classification Part 1: Pre-trained Weights and Data Setup"),
    ("fine-tuning-for-classification-2.html", "Fine-Tuning for Classification Part 2: Modifying the Architecture"),
    ("fine-tuning-for-classification-3.html", "Fine-Tuning for Classification Part 3: Training Loop and Evaluation"),
    ("fine-tuning-to-follow-instructions-1.html", "Fine-Tuning to Follow Instructions Part 1: Instruction Formatting"),
    ("fine-tuning-to-follow-instructions-2.html", "Fine-Tuning to Follow Instructions Part 2: Training and Evaluation")
]

# Let's extract exact titles from the HTML files just to be sure
actual_blogs = []
for filename, fallback_title in blog_list:
    filepath = os.path.join('blogs', filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            match = re.search(r'<h1.*?>(.*?)</h1>', content)
            if match:
                actual_blogs.append((filename, match.group(1)))
            else:
                actual_blogs.append((filename, fallback_title))

# Read the index file
index_path = os.path.join('blogs', 'index.html')
with open(index_path, 'r', encoding='utf-8') as f:
    index_html = f.read()

# Find where to insert
insert_marker = '</a>\n                  </div>\n                </div>'
start_idx = index_html.find('id="llm-children"')
if start_idx == -1:
    print("Could not find llm-children div.")
    exit(1)

insert_idx = index_html.find('</div>', start_idx)
# Let's just find the last </a> before the closing </div> of llm-children
sub_html = index_html[start_idx:]
end_of_children = sub_html.find('</div>')
last_a = sub_html.rfind('</a>', 0, end_of_children) + 4
insert_pos = start_idx + last_a

# Build HTML to insert
insert_content = ""
start_num = 8
for filename, title in actual_blogs:
    insert_content += f'''
                    <a class="tree-file" href="{filename}">
                      <span class="tree-icon">
                        <!-- Retro document SVG outline icon -->
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="#FFFFFF" stroke="#555555" stroke-width="1.5" stroke-linejoin="round">
                          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                          <polyline points="14 2 14 8 20 8" />
                          <line x1="16" y1="13" x2="8" y2="13" stroke-width="1" />
                          <line x1="16" y1="17" x2="8" y2="17" stroke-width="1" />
                          <polyline points="10 9 9 9 8 9" stroke-width="1" />
                        </svg>
                      </span>
                      <span class="tree-name">{start_num}. {title}</span>
                    </a>'''
    start_num += 1

new_index_html = index_html[:insert_pos] + insert_content + index_html[insert_pos:]

# Update the status bar count "6 object(s) in collection" -> "16 object(s) in collection" (actually it was 7 initially, index 1 to 7)
# Let's count actual links inside llm-children
link_count = new_index_html[start_idx:start_idx + new_index_html[start_idx:].find('</div>')].count('<a class="tree-file"')
new_index_html = re.sub(r'<div class="status-panel">\d+ object\(s\) in collection</div>', f'<div class="status-panel">{link_count} object(s) in collection</div>', new_index_html)


with open(index_path, 'w', encoding='utf-8') as f:
    f.write(new_index_html)
print(f"Updated index.html with {len(actual_blogs)} new blogs. Total {link_count} items in collection.")
