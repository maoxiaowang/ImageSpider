# coding=utf-8


class UnknownPythonVersion(Exception):
    msg = 'Unknown Python version found, please check your Python installation.'


class UnsupportedPythonVersion(Exception):
    msg = 'So far ImageSpider only support Python 2.'


class GetBaseLinkFailed(Exception):
    msg = 'Getting base link failed.'


class ParameterNotGiven(Exception):
    msg = 'Parameter is not given.'


class InvalidImageFileName(Exception):
    msg = 'Invalid image filename found.'


class ClearCacheFailed(Exception):
    msg = 'Clearing cache failed.'


class LoadCacheFailed(Exception):
    msg = 'Loading cache failed.'


class InitializeFailed(Exception):
    msg = 'Initialization failed.'


class SaveImageFailed(Exception):
    msg = 'Saving image failed.'


class TranslateToAbsoluteURLFailed(Exception):
    msg = 'Translating relative URL to absolute URL failed.'


class LoadSettingsFileFailed(Exception):
    msg = 'load settings.conf failed, please check if it exists.'


class SettingsError(Exception):
    CONFIG = 'settings.conf: '
    interval_err = CONFIG + '[interval] must be larger than 0.'
    sites_err = CONFIG + '[sites] is necessary.'


class InvalidDomain(Exception):
    msg = 'The domain is invalid.'


class PackageNotInstalled(Exception):
    pass
