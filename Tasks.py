import asyncio
from threading import Thread


class Tasks:
    """Do tasks asynchronously

    Example:
    Tasks(async_loop, lambda: fetch_url(url))

    Arguments:
    loop: Main event loop
    fn: Function to execute
    Source:
    https://stackoverflow.com/questions/47895765/use-asyncio-
    and-tkinter-or-another-gui-lib-together-without-freezing-the-gui
    """
    async_loop = None
    fns = []
    debug = False
    thread: Thread = None

    tasks = []

    def __init__(self, async_loop, fns, debug=False):
        self.async_loop = async_loop
        self.debug = debug

        if self.debug:
            print("/src/utils -> Tasks -> __init__():")

        if type(fns) == type([]):
            self.fns = fns
        else:
            self.fns.append(fns)
        
        self.thread = Thread(target=self._asyncio_thread, args=())
        self.thread.start()
        print("Thread: ", self.thread)

    def join(self):
        if self.debug:
            print("/src/utils/Tasks -> Tasks -> join():")

        if self.thread:
            self.thread.join()
        else:
            print("Thread doesn't exist.")

    async def run_async(self, fn):
        """ Run fns asynchronously"""
        return fn()

    async def run_fns(self):
        """ Creating and starting 10 tasks. """
        if self.debug:
            print("/src/utils/Tasks -> Tasks -> run_fns():")

        self.tasks = [self.run_async(fn) for fn in self.fns]
        number_of_tasks = len(self.tasks)

        if self.debug:
            print("Tasks: ", self.tasks)
        
        # Now that the functions were added to tasks local variable,
        # empty the "fns" array
        self.fns = []
        
        completed, pending = await asyncio.wait(self.tasks)
        results = [task.result() for task in completed]
        
        if self.debug:
            print(f"Tasks completed ({number_of_tasks})!")
        return results

    def _asyncio_thread(self):
        return self.async_loop.run_until_complete(self.run_fns)
