import PySimpleGUI as sg
from view.UserMediator import UserMediator
from controller.Enumerators import Action, Status
from typing import List
from view.ButtonDescription import ButtonDescription


def generate_annotation_buttons(buttons: List[ButtonDescription]) -> List[List[sg.Button]]:
    res = []
    for i in range(0, len(buttons)):
        if buttons[i].get_group_id() != '':
            res.append([sg.Button(buttons[i].get_name(), key=f'-CA{i}-', size=(45, 1)),
                        sg.Radio("", buttons[i].get_group_id(), key=f'-CAR{i}-', disabled=True)])
        else:
            res.append([sg.Button(buttons[i].get_name(), key=f'-CA{i}-', size=(45, 1)),
                        sg.Checkbox("", enable_events=True, key=f'-CAC{i}-', disabled=True)])
    return res


class SelectorView:
    def __init__(self, reason_buttons: List[ButtonDescription], annotation_buttons: List[ButtonDescription], project_folder):
        sg.theme('DarkBlack1')
        self.__project_folder = project_folder
        self.__annotation_buttons = annotation_buttons
        self.__reason_buttons = reason_buttons

        image_column = [[sg.Text("1_1", size=(180, 1), key="-FILENAME-", justification='c')],
                        [sg.Image(f"sources/{project_folder}/cache.png", key="-IMAGE-")]]

        reason_column = [[sg.Text("Progress")],
                         [sg.Text("(0/0)", key="-PROGRESS-")],
                         [sg.Text("Status")],
                         [sg.Text("Not reviewed", key="-STATUS-", font=('', 20),
                                  background_color='gray', size=(25, 1), justification='c')],
                         [sg.Checkbox("Allow shortcuts", enable_events=True, key='-ALLOWSHORTCUTS-')],
                         [sg.Text("Common remove reasons")]]
        reason_column += [[sg.Button(reason_buttons[i].get_name(), key=f'-CR{i}-', size=(45, 1)),
                           sg.Checkbox("", enable_events=True, key=f'-CRC{i}-', disabled=True)]
                          for i in range(0, len(reason_buttons))]
        reason_column += [[sg.Text("Remove reason")],
                         [sg.Multiline(size=(58, 3), key='-REASON-', no_scrollbar=True)],
                         [sg.Text("Common annotations")]]
        reason_column += generate_annotation_buttons(self.__annotation_buttons)
        reason_column += [[sg.Text("Annotation")],
                         [sg.Multiline(size=(58, 3), key='-ANNOTATION-', no_scrollbar=True)],
                         [sg.Button("remove", key="-REMOVE-", size=(11, 1)),
                          sg.Button("keep", key="-KEEP-", size=(11, 1)),
                          sg.Button("previous", key="-PREVIOUS-", size=(11, 1)),
                          sg.Button("next", key="-NEXT-", size=(11, 1))]]

        # Define the window's contents
        self.__layout = [[sg.Column(image_column),  # Part 2 - The Layout
                          sg.Column(reason_column)]]

        self.__window = sg.Window('PainlessLabels', self.__layout, finalize=True, return_keyboard_events=True)  # Part 3 - Window Defintion
        self.__window.Maximize()

    def get_user_input(self, data: UserMediator) -> (UserMediator, bool):
        # Update elements
        self.__window['-PROGRESS-'].update(data.get_progress())
        self.__window['-FILENAME-'].update(data.get_filename())
        self.__window['-IMAGE-'].update(f'sources/{self.__project_folder}/cache.png')
        if data.get_status() == Status.NOT_REVIEWED:
            self.__window['-STATUS-'].update('NOT REVIEWED',  background_color='gray')
        elif data.get_status() == Status.TO_KEEP:
            self.__window['-STATUS-'].update('KEEP',  background_color='green')
        elif data.get_status() == Status.TO_REMOVE:
            self.__window['-STATUS-'].update('REMOVE',  background_color='red')
        self.__window['-ANNOTATION-'].update(data.get_annotation())
        self.__window['-REASON-'].update(data.get_reason())

        # Read input
        while True:
            event, values = self.__window.read()
            if event == sg.WINDOW_CLOSED:
                self.__window.close()
                return data, False

            a_s = values['-ALLOWSHORTCUTS-']

            self.__window['-ANNOTATION-'].update(disabled=a_s)
            self.__window['-REASON-'].update(disabled=a_s)

            # ANNOTATION BUTTONS
            # update window, values
            final_annotation = []
            for i in range(0, len(self.__annotation_buttons)):
                if event == f"-CA{i}-" or (a_s and event == self.__annotation_buttons[i].get_shortcut()):
                    if f'-CAC{i}-' in values:
                        self.__window[f'-CAC{i}-'].update(not values[f'-CAC{i}-'])
                        values[f'-CAC{i}-'] = not values[f'-CAC{i}-']
                    if f'-CAR{i}-' in values:
                        # clear other radio values
                        for j in range(0, len(self.__annotation_buttons)):
                            g_id = self.__annotation_buttons[j].get_group_id()
                            if g_id != '' and g_id == self.__annotation_buttons[i].get_group_id():
                                values[f'-CAR{j}-'] = False
                        # set true current radio
                        self.__window[f'-CAR{i}-'].update(True)
                        values[f'-CAR{i}-'] = True

            # collect values radio/checkbox annotations
            for i in range(0, len(self.__annotation_buttons)):
                if f'-CAC{i}-' in values and values[f'-CAC{i}-']:
                    final_annotation.append(self.__annotation_buttons[i].get_value())
                if f'-CAR{i}-' in values and values[f'-CAR{i}-']:
                    final_annotation.append(self.__annotation_buttons[i].get_value())

            final_annotation = ' '.join([str(elem)+',' for elem in final_annotation])[:-1]
            data.set_annotation(final_annotation)
            self.__window['-ANNOTATION-'].update(final_annotation)

            # REASON BUTTONS
            final_reason = []
            for i in range(0, len(self.__reason_buttons)):
                if event == f"-CR{i}-" or (a_s and event == self.__reason_buttons[i].get_shortcut()):
                    if f'-CRC{i}-' in values:
                        self.__window[f'-CRC{i}-'].update(not values[f'-CRC{i}-'])
                        values[f'-CRC{i}-'] = not values[f'-CRC{i}-']
                if f'-CRC{i}-' in values and values[f'-CRC{i}-']:
                    final_reason.append(self.__reason_buttons[i].get_value())

            final_reason = ' '.join([str(elem) + ',' for elem in final_reason])[:-1]
            data.set_reason(final_reason)
            self.__window['-REASON-'].update(final_reason)

            if event == "-REMOVE-" or (a_s and event == 'r'):
                if values['-REASON-'] == '':
                    self.__window['-REASON-'].update(background_color='red')
                else:
                    self.__window['-REASON-'].update(background_color='#e8dcac')
                    data.set_reason(values['-REASON-'])
                    data.set_action(Action.REMOVE)
                    break
            if event == "-KEEP-" or (a_s and event == 'k'):
                data.set_action(Action.KEEP)
                self.__window['-REASON-'].update('')
                data.set_reason('')
                break
            if event in ["-PREVIOUS-", "Left:37"]:
                data.set_action(Action.PREVIOUS)
                break
            if event in ["-NEXT-", "Right:39"]:
                data.set_action(Action.NEXT)
                break

        data.set_annotation(values['-ANNOTATION-'])
        return data, True
