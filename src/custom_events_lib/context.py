class Context:
    """
    Represents the context of an operation.

    Args:
        activity_name (str): The name of the activity.
        user_name (str): The name of the user.
        environment (dict[str, str]): The environment related parameters, e.g. notebook name.

    Attributes:
        activity_name (str): The name of the activity.
        user_name (str): The name of the user.
        environment (dict[str, str]): The environment related parameters, e.g. notebook name.
    """

    def __init__(self, activity_name: str, user_name: str, environment: dict[str, str]):
        self.activity_name = activity_name
        self.user_name = user_name
        self.environment = environment
