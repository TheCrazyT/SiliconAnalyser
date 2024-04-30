import os

# because debugging in multithread can cause problems (breakpoints don't work)
# I added this method ...
def isSingleThread():
    if "SINGLE_THREAD" not in os.environ:
        return False
    return "1" == os.environ["SINGLE_THREAD"]