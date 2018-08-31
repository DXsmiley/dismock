import enum


SPECIAL_TEST_NAMES = {'all', 'unrun', 'failed'}

class TestRequirementFailure(Exception):
    """ Base calss for the errors that are raised when an expectation is not met """


class NoResponseError(TestRequirementFailure):
    """ Raised when the target bot fails to respond to a message """


class NoReactionError(TestRequirementFailure):
    """ Raised when the target bot failed to react to a message """


class UnexpectedResponseError(TestRequirementFailure):
    """ Raised when the target bot failed to stay silent """


class ErrordResponseError(TestRequirementFailure):
    """ Raised when the target bot produced an error message """


class UnexpectedSuccessError(TestRequirementFailure):
    """ Raised when the target bot failed to produce an error message """


class HumanResponseTimeout(TestRequirementFailure):
    """ Raised when a human fails to assert the result of a test """


class HumanResponseFailure(TestRequirementFailure):
    """ Raised when a human fails a test """


class ResponseDidNotMatchError(TestRequirementFailure):
    """ Raised when the target bot responds with a message that doesn't meet criteria """


class ReactionDidNotMatchError(TestRequirementFailure):
    """ Raised when the target bot reacts with the wrong emoji """


class TestResult(enum.Enum):
    """ Enum representing the result of running a test case """
    UNRUN = 0
    SUCCESS = 1
    FAILED = 2


class Test:
    """ Holds data about a specific test """

    def __init__(self, name: str, func, needs_human: bool = False) -> None:
        if name in SPECIAL_TEST_NAMES:
            raise ValueError('{} is not a valid test name'.format(name))
        self.name = name  # The name of the test
        self.func = func  # The function to run when running the test
        self.last_run = 0  # When the test was last run
        self.result = TestResult.UNRUN  # The result of the test (True or False) or None if it was not run
        self.needs_human = needs_human  # Whether the test requires human interation