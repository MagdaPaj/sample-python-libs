class CustomException1(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class CustomException2(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
