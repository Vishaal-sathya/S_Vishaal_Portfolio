import os
import re
import glob
import shutil
import markdown

FINAL_BLOGS_DIR = 'Final Blogs'
BLOGS_DIR = 'blogs'
IMAGES_DIR = 'images/blogs'
OBSIDIAN_DIR = r'C:\Users\Vishaal\Documents\Obisidian\Build a LLM from Scratch'

# Ensure directories exist
os.makedirs(BLOGS_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

# Build an index of all images in the Obsidian directory
obsidian_images = {}
for root, dirs, files in os.walk(OBSIDIAN_DIR):
    for f in files:
        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            obsidian_images[f] = os.path.join(root, f)

# Template path
TEMPLATE_PATH = os.path.join(BLOGS_DIR, 'implementing-a-gpt-model-part-1.html')
with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
    TEMPLATE = f.read()

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

md_files = glob.glob(os.path.join(FINAL_BLOGS_DIR, '*.md'))

for md_file in md_files:
    print(f"Processing {md_file}...")
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Extract frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---\n', md_content, flags=re.DOTALL)
    title = "Untitled"
    date_val = "2026.08.24"
    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)
        md_content = md_content[frontmatter_match.end():]
        
        title_match = re.search(r'title:\s*"(.*?)"', frontmatter)
        if title_match:
            title = title_match.group(1)
            
        date_match = re.search(r'date:\s*"(.*?)"', frontmatter)
        if date_match:
            date_val = date_match.group(1).replace('-', '.')
            
    slug = slugify(os.path.splitext(os.path.basename(md_file))[0])
    
    # Create image directory for this blog
    blog_img_dir = os.path.join(IMAGES_DIR, slug)
    os.makedirs(blog_img_dir, exist_ok=True)
    
    # Replace images
    def replace_img(match):
        img_name = match.group(1)
        caption = match.group(2)
        
        # Find image in Obsidian
        if img_name in obsidian_images:
            src_path = obsidian_images[img_name]
            dst_path = os.path.join(blog_img_dir, img_name)
            shutil.copy2(src_path, dst_path)
            # Make web path
            web_path = f"../{IMAGES_DIR}/{slug}/{img_name}".replace('\\', '/')
        else:
            print(f"  Warning: Image {img_name} not found in Obsidian folder.")
            web_path = f"../{IMAGES_DIR}/{slug}/{img_name}".replace('\\', '/')
            
        if caption:
            return f'''<div class="blog-image-wrapper">
            <img class="blog-image" src="{web_path}" alt="{caption}" />
            <p class="blog-image-caption">{caption}</p>
          </div>'''
        else:
             return f'''<div class="blog-image-wrapper">
            <img class="blog-image" src="{web_path}" alt="Image" />
          </div>'''
          
    # Regex to catch ![[image.png]] followed by optional *caption*
    md_content = re.sub(r'!\[\[(.*?)\]\](?:\s*\n\*(.*?)\*)?', replace_img, md_content)
    
    # Replace Key Takeaways block
    def replace_takeaways(match):
        items_text = match.group(1)
        items = re.findall(r'> - (.*)', items_text)
        li_elements = ''.join([f'<li>{item}</li>\n' for item in items])
        return f'''<div class="takeaways-box">
            <h4>Key Takeaways</h4>
            <ul>
{li_elements}            </ul>
          </div>'''
    md_content = re.sub(r'> \*\*Key Takeaways\*\*\n((?:> - .*\n?)+)', replace_takeaways, md_content)
    
    # Important/Note block
    def replace_note(match):
        title = match.group(1)
        text = match.group(2)
        return f'''<div class="takeaways-box">
            <h4>{title}</h4>
            <p>{text}</p>
          </div>'''
    md_content = re.sub(r'> \[\!(.*?)\]\n> (.*)', replace_note, md_content)

    # Convert Markdown to HTML
    
    md_content = re.sub(r'(?m)^\s*---\s*$', '', md_content)
    html_content = markdown.markdown(md_content, extensions=['fenced_code', 'tables'])
    
    # Fill Template
    blog_template = TEMPLATE
    
    # Title
    blog_template = re.sub(r'<title>.*?</title>', f'<title>{title} - Vishaal S Blog</title>', blog_template)
    blog_template = re.sub(r'<h1.*?>.*?</h1>', f'<h1>{title}</h1>', blog_template)
    blog_template = re.sub(r'<h2 class="sidebar-title">.*?</h2>', f'<h2 class="sidebar-title">\n          {title}\n        </h2>', blog_template, flags=re.DOTALL)
    
    # Meta
    blog_template = re.sub(r'<span class="metadata-value">\d{4}\.\d{2}\.\d{2}</span>', f'<span class="metadata-value">{date_val}</span>', blog_template)
    
    # Replace the article body
    article_start = blog_template.find('<article class="article-body">')
    if article_start != -1:
        article_start += len('<article class="article-body">')
        article_end = blog_template.find('</article>', article_start)
        
        new_template = blog_template[:article_start] + '\n' + html_content + '\n        ' + blog_template[article_end:]
        
        out_path = os.path.join(BLOGS_DIR, f"{slug}.html")
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(new_template)
        print(f"  -> Saved {out_path}")
    else:
        print(f"  Error: Could not find <article class=\"article-body\"> in template for {md_file}")

print("All done!")
