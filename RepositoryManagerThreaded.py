from threading import Thread, Lock
from queue import Queue
import asyncio

from .RepositoryManager import RepositoryManager


class RepositoryManagerThreaded:
    async_loop = None
    fn = None
    debug: bool = False
    thread: Thread = None

    task = None
    queueA = None

    def __init__(
            self,
            async_loop,
            projects_path,
            username,
            token,
            max_clone_repositories=3,
            git_pull_callback=None,
            git_clone_callback=None,
            debug=False):
        self.async_loop = async_loop
        self.debug = debug

        if self.debug:
            print("/src/utils -> Tasks -> __init__():")

        # Manage repositories, update, pull, etc.
        lock = Lock()
        # Use queueA.empty() to check whether it's empty or not
        self.queueA = Queue()

        self.fn = lambda: RepositoryManager(
            projects_path,
            username,
            token,
            lock,
            self.queueA,
            max_clone_repositories=max_clone_repositories,
            debug=self.debug,
            git_pull_callback=git_pull_callback,
            git_clone_callback=git_clone_callback
        )

        self.thread = Thread(target=self._asyncio_thread)
        self.thread.start()
        if self.debug:
            print("Thread: ", self.thread)

    def join(self):
        """Join thread"""
        if self.debug:
            print("/src/utils/Tasks -> Tasks -> join():")
            print("Putting stop into the queue object")
        self.queueA.put("stop")

        if self.thread:
            if self.debug:
                print("Joining thread")
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

        self.task = self.run_async(self.fn)

        if self.debug:
            print("Task: ", self.task)

        completed, pending = await asyncio.wait([self.task])
        if self.debug:
            print(f"Repository fetch thread done!")
        return completed

    def _asyncio_thread(self):
        return self.async_loop.run_until_complete(self.run_fns())