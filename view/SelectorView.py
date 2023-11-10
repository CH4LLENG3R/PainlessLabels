import PySimpleGUI as sg
from view.UserMediator import UserMediator
from controller.Enumerators import Action, Status


class SelectorView:
    def __init__(self):
        sg.theme('DarkBlack1')

        image_column = [[sg.Text("1_1", size=(180, 1), key="-FILENAME-", justification='c')],
                        [sg.Image("view/cache.png", key="-IMAGE-")]]

        reason_column = [[sg.Text("Progress")],
                         [sg.Text("(0/0)", key="-PROGRESS-")],
                         [sg.Text("Status")],
                         [sg.Text("Not reviewed", key="-STATUS-", font=('', 20),
                                  background_color='gray', size=(25, 1), justification='c')],
                         [sg.Checkbox("Allow shortcuts", enable_events=True, key='-ALLOWSHORTCUTS-')],
                         [sg.Text("Common reasons")],
                         [sg.Button("Child", key="-CR1-", size=(50, 1))],
                         [sg.Button("Position", key="-CR2-", size=(50, 1))],
                         [sg.Text("Reason")],
                         [sg.Multiline(size=(58, 3), key='-REASON-', no_scrollbar=True)],
                         [sg.Text("Common annotations")],
                         [sg.Button("Inverted", key="-CA1-", size=(50, 1))],
                         [sg.Button("Foreign Body", key="-CA2-", size=(50, 1))],
                         [sg.Button("Scoliosis", key="-CA3-", size=(50, 1))],
                         [sg.Text("Annotation")],
                         [sg.Multiline(size=(58, 3), key='-ANNOTATION-', no_scrollbar=True)],
                         [sg.Button("remove", size=(11, 1)), sg.Button("keep", size=(11, 1)),
                          sg.Button("previous", size=(11, 1)), sg.Button("next", size=(11, 1))]]

        # Define the window's contents
        self.__layout = [[sg.Column(image_column),  # Part 2 - The Layout
                          sg.Column(reason_column)]]

        self.__window = sg.Window('GUI Selector', self.__layout, finalize=True, return_keyboard_events=True)  # Part 3 - Window Defintion
        self.__window.Maximize()

    def get_user_input(self, data: UserMediator) -> (UserMediator, bool):
        # Update elements
        self.__window['-PROGRESS-'].update(data.get_progress())
        self.__window['-FILENAME-'].update(data.get_filename())
        self.__window['-IMAGE-'].update('view/cache.png')
        if data.get_status() == Status.NOT_REVIEWED:
            self.__window['-STATUS-'].update('NOT REVIEWED',  background_color='gray')
        elif data.get_status() == Status.TO_KEEP:
            self.__window['-STATUS-'].update('KEEP',  background_color='green')
        elif data.get_status() == Status.TO_REMOVE:
            self.__window['-STATUS-'].update('REMOVE',  background_color='red')
        self.__window['-REASON-'].update(data.get_reason())
        self.__window['-ANNOTATION-'].update(data.get_annotation())

        # Read input
        while True:
            event, values = self.__window.read()
            a_s = values['-ALLOWSHORTCUTS-']

            if a_s:
                self.__window['-REASON-'].update(disabled=True)
                self.__window['-ANNOTATION-'].update(disabled=True)
            else:
                self.__window['-REASON-'].update(disabled=False)
                self.__window['-ANNOTATION-'].update(disabled=False)
            print(event, values)
            print(type(event), values)

            if event == sg.WINDOW_CLOSED:
                self.__window.close()
                return data, False
            if event == "-CR1-" or (a_s and event == 'c'):
                self.__window['-REASON-'].update('Child')
                data.set_reason('Child')
            if event == "-CR2-" or (a_s and event == 'p'):
                self.__window['-REASON-'].update('Position')
                data.set_reason('Position')
            if event == "-CA1-" or (a_s and event == 'i'):
                if len(data.get_annotation()) > 0:
                    data.set_annotation(values['-ANNOTATION-']+', Inverted')
                else:
                    data.set_annotation('Inverted')
                self.__window['-ANNOTATION-'].update(data.get_annotation())
            if event == "-CA2-" or (a_s and event == 'f'):
                if len(data.get_annotation()) > 0:
                    data.set_annotation(values['-ANNOTATION-']+', Foreign Body')
                else:
                    data.set_annotation('Foreign Body')
                self.__window['-ANNOTATION-'].update(data.get_annotation())
            if event == "-CA3-" or (a_s and event == 's'):
                if len(data.get_annotation()) > 0:
                    data.set_annotation(values['-ANNOTATION-']+', Scoliosis')
                else:
                    data.set_annotation('Scoliosis')
                self.__window['-ANNOTATION-'].update(data.get_annotation())
            if event == "remove" or (a_s and event == 'r'):
                if values['-REASON-'] == '':
                    self.__window['-REASON-'].update(background_color='red')
                else:
                    self.__window['-REASON-'].update(background_color='#e8dcac')
                    data.set_reason(values['-REASON-'])
                    data.set_action(Action.REMOVE)
                    break
            if event == "keep" or (a_s and event == 'k'):
                data.set_action(Action.KEEP)
                self.__window['-REASON-'].update('')
                data.set_reason('')
                break
            if event in ["previous", "Left:37"]:
                data.set_action(Action.PREVIOUS)
                break
            if event in ["next", "Right:39"]:
                data.set_action(Action.NEXT)
                break

        data.set_annotation(values['-ANNOTATION-'])
        return data, True
