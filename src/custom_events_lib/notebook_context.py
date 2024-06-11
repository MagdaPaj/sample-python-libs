class NotebookContext:
    """
    Represents the context of a notebook.

    Args:
        notebook_name (str): The name of the notebook.
        activity_id (str): The ID of the activity.
        is_for_pipeline (bool): Indicates whether the notebook is for a pipeline.
        user_name (str): The name of the user.

    Attributes:
        notebook_name (str): The name of the notebook.
        activity_id (str): The ID of the activity.
        is_for_pipeline (bool): Indicates whether the notebook is for a pipeline.
        user_name (str): The name of the user.
    """

    def __init__(self, notebook_name: str, activity_id: str, is_for_pipeline: str, user_name: str):
        self.notebook_name = notebook_name
        self.activity_id = activity_id
        self.is_for_pipeline = is_for_pipeline
        self.user_name = user_name
