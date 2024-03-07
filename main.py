from controller.SelectorController import SelectorController
from model.ImageReader import ImageReader
from ProjectManager import ProjectManager
import os
import shutil

print('Welcome to \n')
print('''$$$$$$$\         $$\         $$\                           $$\              $$\               $$\          
$$  __$$\        \__|        $$ |                          $$ |             $$ |              $$ |         
$$ |  $$ $$$$$$\ $$\$$$$$$$\ $$ |$$$$$$\  $$$$$$$\ $$$$$$$\$$ |     $$$$$$\ $$$$$$$\  $$$$$$\ $$ |$$$$$$$\ 
$$$$$$$  \____$$\$$ $$  __$$\$$ $$  __$$\$$  _____$$  _____$$ |     \____$$\$$  __$$\$$  __$$\$$ $$  _____|
$$  ____/$$$$$$$ $$ $$ |  $$ $$ $$$$$$$$ \$$$$$$\ \$$$$$$\ $$ |     $$$$$$$ $$ |  $$ $$$$$$$$ $$ \$$$$$$\  
$$ |    $$  __$$ $$ $$ |  $$ $$ $$   ____|\____$$\ \____$$\$$ |    $$  __$$ $$ |  $$ $$   ____$$ |\____$$\ 
$$ |    \$$$$$$$ $$ $$ |  $$ $$ \$$$$$$$\$$$$$$$  $$$$$$$  $$$$$$$$\$$$$$$$ $$$$$$$  \$$$$$$$\$$ $$$$$$$  |
\__|     \_______\__\__|  \__\__|\_______\_______/\_______/\________\_______\_______/ \_______\__\_______/ \n''')
print('The dev was lazy and did not implement graphical user interface for this part...')
print('Dont worry, I will ask you a few questions and an interface made by Pablo Picasso himself will show up ;)\n')


def __main__():
    pm = ProjectManager()
    while True:
        print('1. Continue labeling')
        print('2. Download new dataset')
        choice = int(input("choice: "))

        if choice == 1:
            project = pm.choose_from_existing()
            if project != '':
                break
        elif choice == 2:
            try:
                pm.download_new()
            except ResourceWarning as e:
                print(e)
                continue
            project = pm.get_project_name()
            break

    controller = SelectorController(ImageReader, project)
    pm.create_copy()
    if controller.is_completed():
        pm.upload_result(project)
        shutil.rmtree("sources")


__main__()
