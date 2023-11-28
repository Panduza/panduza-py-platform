import abc
import asyncio

class PlatformWorker(metaclass=abc.ABCMeta):
    """Mother class for all platform objects
    """

    # ---

    def __init__(self, platform = None) -> None:
        """Constructor
        """
        # Alive flag for the work (must stop if == False)
        self.alive = True

        # Store platform access
        self.platform = platform

        # Task managed by this worker
        self._subTasks = []

    # ---

    def stop(self):
        self.cancel_all_tasks()
        self.alive = False

    # ---

    def load_worker_task(self, coro, name = None):        
        if name == None:
            name=f"FROM>{self.PZA_WORKER_name()}"
        new_task = self.platform.load_task(coro, name)
        self._subTasks.append(new_task)
        return new_task

    # ---

    def cancel_all_tasks(self):
        for t in self._subTasks:
            t.cancel()

    # ---

    async def worker_panic(self):
        await self.platform.handle_worker_panic(self.PZA_WORKER_name(), self.PZA_WORKER_status())

    # ---

    async def task(self):
        """Main task loop
        """
        while(self.alive):
            await asyncio.sleep(0.1)
            await self.PZA_WORKER_task()

        await self.PZA_WORKER_dying_gasp()
        self.PZA_WORKER_log().info("stopped")

    # =============================================================================
    # OVERRIDE REQUESTED FUNCTIONS

    # ---

    @abc.abstractmethod
    def PZA_WORKER_name(self):
        """
        """
        pass

    # ---

    @abc.abstractmethod
    def PZA_WORKER_log(self):
        """
        """
        pass

    # ---

    @abc.abstractmethod
    def PZA_WORKER_status(self):
        """Return a state report of the worker
        To be able to indicate to administrator why the platform stopped
        """
        pass

    # ---

    @abc.abstractmethod
    async def PZA_WORKER_task(self):
        """
        """
        pass

    # ---

    async def PZA_WORKER_dying_gasp(self):
        """Provide a way for the worker to execute a last action before stopping
        """
        pass

    # ---
