from jinja2 import Environment, FileSystemLoader
import os
import shutil
import markdown

#
# Recursively deletes all children of a directory, but does not delete the root 
#
def delete_dir(dir, root):
    if os.path.exists(dir):
        for file in os.listdir(dir):
            full_path = os.path.join(dir, file)

            if os.path.isdir(full_path):
                delete_dir(full_path, False)
            else:
                os.remove(full_path) 

        if not root:
            os.rmdir(dir)


#
# Recursively finds html files in dir, except for in the excluded directories
#
def find_templates(dir, excluding):
    templates = []

    if os.path.exists(dir) and os.path.basename(dir) not in excluding:
        for file in os.listdir(dir):
            full_path = os.path.join(dir, file)

            if os.path.isdir(full_path):
                temp = find_templates(full_path, excluding)

                if len(temp) > 0: 
                    templates.extend(temp)

            else:

                if os.path.basename(file).split(".")[-1] == "html":
                    templates.append(full_path.replace("\\", "/"))

    return templates

#
# Reads all markdown files from dir, converts the markdown to HTML, and returns as a dictionary
# Does not support nested directories
#
def get_blog_posts(dir):
    if not os.path.isdir(dir):
        return dict()

    result = dict()

    for file in os.listdir(dir):
        path = os.path.join(dir, file)

        if not os.path.isfile(path):
            continue

        text = ""
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        html = markdown.markdown(text, extensions=['extra'])

        result[file] = html

    return result


#
# Takes a dictionary of blog posts where the md file name is the key and the post content is the value
# and creates a new template file for each post. Templates are placed in web/blog/<file_name>
#
def make_blog_post_templates(posts):
    template_str = """{{% extends 'templates/blog-post.html' %}}
{{% block content %}} 
{}
{{% endblock %}}
"""

    for key, val in posts.items():
        file_name = key.replace('.md', '')
        folder_path = os.path.join("web", "blog", file_name)
        file_path = os.path.join(folder_path, "index.html")
        file_content = template_str.format(val)

        if os.path.exists(file_path):
            os.remove(file_path)

        if not os.path.exists(folder_path):
            os.mkdir(folder_path)

        with open(file_path, "w") as f:
            f.write(file_content)



def main():
    template_dir = "web"
    output_dir = "out"
    blog_post_dir = "posts"

    # Folders inside template_dir to copy without modification
    static_folders = ["css", "images", "js"]

    posts = get_blog_posts(blog_post_dir)
    make_blog_post_templates(posts)


    # Render and output the templates
    pages = find_templates(template_dir, ["templates"]) 
    for i, page in enumerate(pages):
        pages[i] = page.replace("web/", "")


    delete_dir(output_dir, True)

    env = Environment(loader=FileSystemLoader(template_dir))

    for page in pages:
        template = env.get_template(page)
        content = template.render()

        dirs = page.split("/")[0:-1]
        file = page.split("/")[-1]
        page_output_dir = output_dir
        if len(dirs) > 0:
            page_output_dir = os.path.join(output_dir, os.path.join(*dirs))
            if not os.path.exists(page_output_dir):
                os.makedirs(page_output_dir)

        with open(os.path.join(page_output_dir, file), "+w") as f:
            f.write(content)


    # Copy the static files
    for folder in static_folders:
        shutil.copytree(template_dir + "/" + folder, os.path.basename(output_dir) + "/" + folder)





#
# PROGRAM ENTRY
#
main()
    


                


