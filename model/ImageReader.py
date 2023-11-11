from model.ImageReaderInterface import ImageReaderInterface
import os
from PIL import Image


class ImageReader(ImageReaderInterface):
    def __init__(self, path: str):
        if not os.path.isdir(path):
            raise Exception('Path {} not found'.format(path))
        self.__i = -1
        self.__files = [f for f in os.listdir(path)]
        self.__files.sort()
        self.__length = len(self.__files)
        self.__path = path
        if not (self.__path.endswith('/') or self.__path.endswith('\\')):
            self.__path += '/'

    def __load(self):
        im1 = Image.open(self.__path+self.__files[self.__i])
        shape = im1.size
        scale = 2
        im1.resize((int(shape[0]*scale), int(shape[1]*scale))).save('sources/cache.png')

    def load_next(self):
        if self.__i < self.__length - 1:
            self.__i += 1
            self.__load()

    def load_previous(self):
        if self.__i > 0:
            self.__i -= 1
            self.__load()

    def get_dataset_length(self) -> int:
        return self.__length

    def get_current_filename(self) -> str:
        if self.__i < 0:
            return self.__files[0]
        if self.__i > self.__length:
            return self.__files[-1]
        return self.__files[self.__i]

    def load_specific(self, name):
        self.__i = self.__files.index(name)
        self.__load()

    def get_length(self) -> int:
        return self.__length
