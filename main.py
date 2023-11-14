from controller.SelectorController import SelectorController
from model.ImageReader import ImageReader
from ProjectManager import ProjectManager
import os

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


def choose_from_existing() -> str:
    local_projects = os.listdir('sources')
    if len(local_projects) == 0:
        print('no local projects yet')
        input('Press Enter to continue...')
        return ''
    for i in range(0, len(local_projects)):
        print(f'{i+1}: {local_projects[i]}')
    while True:
        choice = int(input('choose: '))
        if 1 <= choice <= len(local_projects) + 1:
            return local_projects[choice - 1]
        print('incorrect choice.')


def __main__():
    pm = ProjectManager()
    project = ''
    while True:
        print('1. Continue labeling')
        print('2. Download new dataset')
        choice = int(input("choose: "))

        if choice == 1:
            project = choose_from_existing()
            if project != '':
                break
        elif choice == 2:
            pm.download_new()
            project = pm.get_project_name()
            break

    controller = SelectorController(ImageReader, project)
    pm.upload_result(project)

__main__()

