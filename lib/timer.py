import time

class Timer:
    def __init__(self, operation):
        self.operation = operation
    def __enter__(self): self.start = time.time()
    def __exit__(self, *args): print self.operation, ",", time.time() - self.start

# Usage:
# with Time("message"):
#    runThis()
# Returns time in seconds.
