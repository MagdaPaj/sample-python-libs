class CustomException1(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class CustomException3(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class CustomException4(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
