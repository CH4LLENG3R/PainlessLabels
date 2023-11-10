from view.SelectorView import SelectorView
from model.ImageReaderInterface import ImageReaderInterface
from view.UserMediator import UserMediator
from controller.Enumerators import Action, Status
import os
import pandas as pd


class SelectorController:
    def __perform_action(self, data: UserMediator) -> UserMediator:
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
        pd.to_pickle(self.__df, 'output/UCK_output.pkl')
        print(self.__df)

        # Read new
        if data.get_action() in [Action.KEEP, Action.REMOVE, Action.NEXT]:
            self.__im_reader.load_next()
        elif data.get_action() == Action.PREVIOUS:
            self.__im_reader.load_previous()

        new_filename = self.__im_reader.get_current_filename()
        data = UserMediator(filename=new_filename, status=Status.NOT_REVIEWED)
        if new_filename in self.__df.index:
            row = self.__df.loc[self.__df.index == new_filename]
            data = UserMediator(filename=new_filename, status=Status[row['Status'][0]], reason=row['Reason'][0],
                                annotation=row['Annotation'][0])

        done_count = self.__df[self.__df.Status == 'TO_KEEP'].shape[0] + self.__df[self.__df.Status == 'TO_REMOVE'].shape[0]
        data.set_progress('({}/{})'.format(done_count, self.__im_reader.get_length()))

        return data

    def __init__(self, im_reader: ImageReaderInterface):
        self.__view = SelectorView()

        self.__im_reader = im_reader
        self.__df = pd.DataFrame(columns=['Filename', 'Status', 'Reason', 'Annotation']).set_index(['Filename'])

        self.__im_reader.load_next()
        data = UserMediator(filename=self.__im_reader.get_current_filename())
        if os.path.isfile('output/UCK_output.pkl'):
            self.__df = pd.read_pickle('output/UCK_output.pkl')
            last_row = self.__df.iloc[-1:]
            data = UserMediator(filename=last_row.index[0], status=Status[last_row['Status'][0]],
                                reason=last_row['Reason'][0],
                                annotation=last_row['Annotation'][0])
            self.__im_reader.load_specific(data.get_filename())

        print(self.__df)
        loop = True
        while loop:
            data, loop = self.__view.get_user_input(data)
            if not loop:
                break
            data = self.__perform_action(data)

        pd.to_pickle(self.__df, 'output/UCK_output.pkl')
