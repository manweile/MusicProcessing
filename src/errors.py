class MusicProcessingException(Exception):
    '''
    @brief Base class for any MusicProcessing Exception
    '''

    def __init__(self, message="A MusicProcessingException occurred"):
        self.message = message
        super().__init__(self.message)


class FfmpegProcessError(MusicProcessingException):
    '''
    @brief Indicates error occurred processing a ffmpeg command.
    '''

    def __init__(self, message="A FfmpegError occurred"):
        self.message = message
        super().__init__(self.message)


class JSONOutputError(MusicProcessingException):
    '''
    @brief Indicates error occurred finding json output.
    '''

    def __init__(self, message="A JSONOutputError occurred"):
        self.message = message
        super().__init__(self.message)


class MetadataTypeError(MusicProcessingException):
    '''
    @brief Indicates a non-standard metadata type was encountered.
    '''

    def __init__(self, message="A MetadataTypeError occurred"):
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
    @brief Indicates directory_processing.path_info function returned None.
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


class VideoStreamError(MusicProcessingException):
    '''
    @brief Indicates an error occurred in audio_art.had_video_stream function.
    '''

    def __init__(self, message="A VideoStreamError occurred"):
        self.message = message
        super().__init__(self.message)
