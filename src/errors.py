'''
@module errors
@file errors.py
@author Gerald Manweiler

@brief Defines the errors module

@details Defines the custom exceptions used in the MusicProcessing module.

@note This implementation does not require garbage collection or logging functionality.

@version 1.0.0
@date 2024-06-05

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''


class MusicProcessingException(Exception):
    '''
    @brief Base class for any MusicProcessing Exception

    @details Base class for all custom exceptions in the MusicProcessing module.
    '''

    def __init__(self, message="A MusicProcessingException occurred"):
        '''
        @brief Initializes the MusicProcessingException class.

        @details Initializes the MusicProcessingException with the provided error message.

        @param message {str} The error message.
        '''

        self.message = message
        super().__init__(self.message)


class FfmpegProcessError(MusicProcessingException):
    '''
    @brief Base class for ffmpeg processing errors.

    @details Base class for all ffmpeg processing errors in the MusicProcessing module.
    '''

    def __init__(self, message="A FfmpegError occurred"):
        '''
        @brief Initializes the FfmpegProcessError class.

        @details Initializes the FfmpegProcessError with the provided error message.

        @param message {str} The error message.
        '''

        self.message = message
        super().__init__(self.message)


class JSONOutputError(MusicProcessingException):
    '''
    @brief Base class for JSON output errors.

    @details Base class for all JSON output errors in the MusicProcessing module.
    '''

    def __init__(self, message="A JSONOutputError occurred"):
        '''
        @brief Initializes the JSONOutputError class.

        @details Initializes the JSONOutputError with the provided error message.

        @param message {str} The error message.
        '''

        self.message = message
        super().__init__(self.message)


class MetadataTypeError(MusicProcessingException):
    '''
    @brief Base class for metadata type errors.

    @details Base class for all metadata type errors in the MusicProcessing module.
    '''

    def __init__(self, message="A MetadataTypeError occurred"):
        '''
        @brief Initializes the MetadataTypeError class.

        @details Initializes the MetadataTypeError with the provided error message.

        @param message {str} The error message.
        '''

        self.message = message
        super().__init__(self.message)


class MusicProcessingError(MusicProcessingException):
    '''
    @brief Base class for generic music processing errors.

    @details Base class for all generic music processing errors in the MusicProcessing module.
    '''

    def __init__(self, message="A MusicProcessingError occurred"):
        '''
        @brief Initializes the MusicProcessingError class.

        @details Initializes the MusicProcessingError with the provided error message.

        @param message {str} The error message.
        '''

        self.message = message
        super().__init__(self.message)


class PathInfoError(MusicProcessingException):
    '''
    @brief Base class for path info errors.

    @details Base class for all path info errors in the MusicProcessing module.
    '''

    def __init__(self, message="A PathInfoError occurred"):
        '''
        @brief Initializes the PathInfoError class.

        @details Initializes the PathInfoError with the provided error message.

        @param message {str} The error message.
        '''

        self.message = message
        super().__init__(self.message)


class PlaylistError(MusicProcessingException):
    '''
    @brief Base class for playlist errors.

    @details Base class for all playlist errors in the MusicProcessing module.

    @param message {str} The error message.
    '''

    def __init__(self, message="A PlaylistError occurred"):
        '''
        @brief Initializes the PlaylistError class.

        @details Initializes the PlaylistError with the provided error message.

        @param message {str} The error message.
        '''

        self.message = message
        super().__init__(self.message)


class VideoStreamError(MusicProcessingException):
    '''
    @brief Base class for video stream errors.

    @details Base class for all video stream errors in the MusicProcessing module.
    '''

    def __init__(self, message="A VideoStreamError occurred"):
        '''
        @brief Initializes the VideoStreamError class.

        @details Initializes the VideoStreamError with the provided error message.

        @param message {str} The error message.
        '''

        self.message = message
        super().__init__(self.message)
