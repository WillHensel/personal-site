from jinja2 import Environment, FileSystemLoader
import os
import shutil

#
# Recursively deletes all children of a directory and then deletes the directory
#
def delete_dir(dir, root):
    if (os.path.exists(dir)):
        for file in os.listdir(dir):
            full_path = os.path.join(dir, file)
            if os.path.isdir(full_path):
                delete_dir(full_path, False)
            else:
                os.remove(full_path) 
        if not root:
            os.rmdir(dir)


#
# Recursively finds html files in dir, except for in the excluding dir
#
def find_templates(dir, excluding):
    templates = []
    if (os.path.exists(dir) and os.path.basename(dir) != excluding):
        for file in os.listdir(dir):
            full_path = os.path.join(dir, file)
            if os.path.isdir(full_path):
                temp = find_templates(full_path, excluding)
                if (len(temp) > 0): 
                    templates.extend(temp)
            else:
                if (os.path.basename(file).split(".")[-1] == "html"):
                    templates.append(full_path.replace("\\", "/"))
    return templates



template_dir = "web"
output_dir = "out"
static_folders = ["css", "images", "js"]


pages = find_templates(template_dir, "templates") 
for i, page in enumerate(pages):
    pages[i] = page.replace("web/", "")


env = Environment(loader=FileSystemLoader(template_dir))

delete_dir(output_dir, True)
# os.mkdir(output_dir)


# Render and output the templates
for page in pages:
    template = env.get_template(page)
    content = template.render()

    dirs = page.split("/")[0:-1]
    file = page.split("/")[-1]
    page_output_dir = output_dir
    if len(dirs) > 0:
        page_output_dir = os.path.join(output_dir, str.join("/", dirs))
        if not os.path.exists(page_output_dir):
            os.mkdir(page_output_dir)

    with open(os.path.join(page_output_dir, file), "+w") as f:
        f.write(content)


# Copy the static files
for folder in static_folders:
    shutil.copytree(template_dir + "/" + folder, os.path.basename(output_dir) + "/" + folder)
    


                


