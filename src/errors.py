class PathInfoError(Exception):
    '''
    @brief Indicates an error occurred in  path_info function
    '''

    def __init__(self, message="A PathInfoError occurred"):
        self.message = message
        super().__init__(self.message)


class JSONOutputError(Exception):
    '''
    @brief
    '''
    pass


class MusicProcessingError(Exception):
    '''
    @brief Generic
    '''
    pass
