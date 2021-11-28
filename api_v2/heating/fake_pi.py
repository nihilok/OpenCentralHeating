


class FakePi:

    def read(self, *args, **kwargs):
        return 1

    def write(self, *args, **kwargs):
        pass

fake_pi = FakePi