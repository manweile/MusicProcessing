class MusicProcessingException(Exception):
    '''
    @brief Base class for any MusicProcessing Exception
    '''


class JSONOutputError(MusicProcessingException):
    '''
    @brief Indicates error occurred finding json output.
    '''

    def __init__(self, message="A JSONOutputError occurred"):
        self.message = message
        super().__init__(self.message)


class MusicProcessingError(MusicProcessingException):
    '''
    @brief Indicates a generic music processing error occurred.
    '''

    def __init__(self, message="A MusicProcessingError occurred"):
        self.message = message
        super().__init__(self.message)


class PathInfoError(MusicProcessingException):
    '''
    @brief Indicates an error occurred in  path info function.
    '''

    def __init__(self, message="A PathInfoError occurred"):
        self.message = message
        super().__init__(self.message)


class PlaylistError(MusicProcessingException):
    '''
    @brief Indicates an error occurred in playlist class.
    '''

    def __init__(self, message="A PlaylistError occurred"):
        self.message = message
        super().__init__(self.message)
