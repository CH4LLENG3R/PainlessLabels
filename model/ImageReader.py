import PIL

from model.ImageReaderInterface import ImageReaderInterface
import os
from PIL import Image


class ImageReader(ImageReaderInterface):
    def __load(self) -> bool:
        try:
            im1 = Image.open(self.__path+self.__files[self.__i])
        except PIL.UnidentifiedImageError as e:
            return False

        shape = im1.size
        max_size = 800
        scale = 1
        if shape[0] > shape[1]:
            scale = 1100/shape[0]
        else:
            scale = 1100/shape[1]
        im1.resize((int(shape[0]*scale), int(shape[1]*scale))).save(f'{self.__cache_path}cache.png')
        return True

    def load_next(self) -> bool:
        if self.__i < self.__length - 1:
            self.__i += 1
            return self.__load()
        return True

    def load_previous(self) -> bool:
        if self.__i > 0:
            self.__i -= 1
            return self.__load()
        return True

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

    def get_position(self):
        return self.__i

    def __init__(self, path: str, cache_path: str):
        if not os.path.isdir(path):
            raise Exception('Path {} not found'.format(path))
        if not os.path.isdir(cache_path):
            raise Exception('Path {} not found'.format(path))
        self.__i = -1
        self.__files = [f for f in os.listdir(path)]
        self.__files.sort()
        self.__length = len(self.__files)
        self.__path = path
        self.__cache_path = cache_path
        if not (self.__path.endswith('/') or self.__path.endswith('\\')):
            self.__path += '/'
        if not (self.__cache_path.endswith('/') or self.__cache_path.endswith('\\')):
            self.__cache_path += '/'
