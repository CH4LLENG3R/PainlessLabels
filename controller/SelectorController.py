from view.SelectorView import SelectorView
from model.ImageReaderInterface import ImageReaderInterface
from view.UserMediator import UserMediator
from controller.Enumerators import Action, Status
import os
import pandas as pd
from configparser import ConfigParser
from view.ButtonDescription import ButtonDescription
import json


class SelectorController:

    def __handle_corrupted_image(self):
        self.__df.loc[self.__im_reader.get_current_filename()] = [Status.TO_REMOVE.name, 'Corrupted', 'Corrupted']
        self.__df.to_csv(self.__output_path)

    def __perform_action(self, data: UserMediator) -> (UserMediator, bool):
        # Before Save
        if data.get_action() == Action.KEEP:
            data.set_status(Status.TO_KEEP)
        elif data.get_action() == Action.REMOVE:
            data.set_status(Status.TO_REMOVE)
        elif data.get_action() == Action.PREVIOUS:
            if data.get_status() is None:
                data.set_status(Status.NOT_REVIEWED)
        elif data.get_action() == Action.NEXT:
            if data.get_status() is None:
                data.set_status(Status.NOT_REVIEWED)

        # Save progress
        self.__df.loc[data.get_filename()] = [data.get_status().name, data.get_reason(), data.get_annotation()]
        self.__df.to_csv(self.__output_path)

        # Read new
        if data.get_action() in [Action.KEEP, Action.REMOVE, Action.NEXT]:
            while not self.__im_reader.load_next():
                self.__handle_corrupted_image()
        elif data.get_action() == Action.PREVIOUS:
            while not self.__im_reader.load_previous():
                self.__handle_corrupted_image()

        new_filename = self.__im_reader.get_current_filename()
        data = UserMediator(filename=new_filename, status=Status.NOT_REVIEWED, position=self.__im_reader.get_position())
        if new_filename in self.__df.index:
            row = self.__df.loc[self.__df.index == new_filename]
            data = UserMediator(filename=new_filename, status=Status[row['Status'][0]], reason=row['Reason'][0],
                                annotation=row['Annotation'][0], position=self.__im_reader.get_position())

        done_count = self.__df[self.__df.Status == 'TO_KEEP'].shape[0] + self.__df[self.__df.Status == 'TO_REMOVE'].shape[0]
        data.set_progress('({}/{})'.format(done_count, self.__im_reader.get_dataset_length()))

        if done_count == self.__im_reader.get_dataset_length():
            if not self.__completed:
                self.__continue_after_completed = self.__view.show_completed_message()
            self.__completed = True
            return data, not self.__continue_after_completed
        else:
            return data, True

    def __init__(self, im_reader, project_folder):
        self.__completed = False
        self.__continue_after_completed = False
        # read setup
        config = ConfigParser()
        config.read(f'sources/{project_folder}/config/config.ini')

        ann_buttons_config = config['annotation_buttons']
        rsn_buttons_config = config['reason_buttons']
        paths = config['paths']

        self.__im_reader = im_reader(paths['dataset_path'], f'sources/{project_folder}/')
        self.__im_reader.load_next()

        # parameters
        self.__output_path = paths['output_path']

        ann_buttons = []
        for entry in ann_buttons_config:
            d = json.loads(ann_buttons_config[entry])
            if 'group_id' in d.keys():
                ann_buttons.append(ButtonDescription(d['name'], d['value'], d['shortcut'], d['group_id']))
            else:
                ann_buttons.append(ButtonDescription(d['name'], d['value'], d['shortcut'], ''))

        rsn_buttons = []
        for entry in rsn_buttons_config:
            d = json.loads(rsn_buttons_config[entry])
            rsn_buttons.append(ButtonDescription(d['name'], d['value'], d['shortcut'], ''))

        # initialize view
        self.__view = SelectorView(rsn_buttons, ann_buttons, project_folder)

        # initialize file handling
        if not os.path.exists(os.path.dirname(self.__output_path)):
            os.makedirs(os.path.dirname(self.__output_path))

        self.__df = pd.DataFrame(columns=['Filename', 'Status', 'Reason', 'Annotation']).set_index(['Filename'])

        data = UserMediator(filename=self.__im_reader.get_current_filename())
        if os.path.isfile(self.__output_path):
            self.__df = pd.read_csv(self.__output_path).set_index(['Filename']).fillna('')
            if len(self.__df.index) > 0:
                last_row = self.__df.tail(1)
                data = UserMediator(filename=last_row.index[0], status=Status[last_row['Status'][0]],
                                    reason=last_row['Reason'][0],
                                    annotation=last_row['Annotation'][0])
                self.__im_reader.load_specific(data.get_filename())
                done_count = self.__df[self.__df.Status == 'TO_KEEP'].shape[0] + \
                             self.__df[self.__df.Status == 'TO_REMOVE'].shape[0]
                data.set_progress('({}/{})'.format(done_count, self.__im_reader.get_dataset_length()))
                data.set_position(self.__im_reader.get_position())

        loop = True
        while loop:
            data, loop = self.__view.get_user_input(data)
            if not loop:
                break
            data, loop = self.__perform_action(data)
        self.__df.to_csv(self.__output_path)

    def is_completed(self) -> bool:
        return self.__completed
