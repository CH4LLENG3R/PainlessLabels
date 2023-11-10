from model import ImageReaderInterface


class ExampleImageReader(ImageReaderInterface):
    def __init__(self):
        self.__i = -1

    def load_next(self):
        self.__i += 1
        print('Image swapped for file_{}'.format(self.__i))

    def load_previous(self):
        self.__i -= 1
        print('Image swapped for file_{}'.format(self.__i))

    def get_dataset_length(self) -> int:
        return 1000

    def get_current_filename(self) -> str:
        return 'file_{}'.format(self.__i)

    def load_specific(self, name):
        print('Image swapped for {}'.format(name))
