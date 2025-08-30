"""Copyright (c) 2023 Aydin Abdi

This module defines the base class for exceptions in this module.

Example:
    raise ATSLinterError("This is an error message.")
"""


class ATSLinterError(Exception):
    """Base class for exceptions in this module.

    Parameters:
        message: The error message.
    """

    def __init__(self, message: str):
        """Initialize an MHSTestLintError object.

        Args:
            message: The error message.
        """
        super().__init__(message)
        self.message = message


class ATSFileCollectionError(ATSLinterError):
    """Exception raised for errors in file collection."""
    pass


class ATSASTParseError(ATSLinterError):
    """Exception raised for errors in AST parsing."""
    pass
