class ImageReaderInterface:
    def load_next(self):
        raise NotImplementedError('Not implemented.')

    def load_previous(self):
        raise NotImplementedError('Not implemented.')

    def get_dataset_length(self) -> int:
        raise NotImplementedError('Not implemented.')

    def get_current_filename(self) -> str:
        raise NotImplementedError('Not implemented.')

    def load_specific(self, name):
        raise NotImplementedError('Not implemented.')
