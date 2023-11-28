import asyncio
import threading
import sys

# ---

class MonitoredEventLoop(asyncio.SelectorEventLoop):
    """Event loop that provide some load metric
    """

    # ---

    def __init__(self, platform, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._total_time = 0
        self._select_time = 0

        self._before_select = None
        
        self.platform = platform
        self.log = self.platform.log
        self.perf_cycle_time = 2

        # self.log.info(f"EVENT LOOP UP !!")

    # ---

    # TOTAL TIME:
    def run_forever(self):
        self.ref_time = self.time()
        try:
            self.log.info(f"EVENT LOOP RUN")
            self._check_closed()
            self._check_running()
            self._set_coroutine_origin_tracking(self._debug)
            self._thread_id = threading.get_ident()

            old_agen_hooks = sys.get_asyncgen_hooks()
            sys.set_asyncgen_hooks(firstiter=self._asyncgen_firstiter_hook,
                                finalizer=self._asyncgen_finalizer_hook)
            try:
                asyncio.events._set_running_loop(self)
                
                while True:
                    try:
                        # self.log.info(f"ONE")
                        self._run_once()
                        if self._stopping:
                            break
                    except KeyboardInterrupt:
                        self.log.warning("ctrl+c => user stop requested !!!!!!!!!!!! XD")
                        # self._stopping = True
                        self.platform.stop()
            finally:
                self._stopping = False
                self._thread_id = None
                asyncio.events._set_running_loop(None)
                self._set_coroutine_origin_tracking(False)
                sys.set_asyncgen_hooks(*old_agen_hooks)
        finally:
            finished = self.time()
            # self._total_time = finished - started

    # ---

    # SELECT TIME:
    def _run_once(self):
        # print("_run_once")
        self._before_select = self.time()
        super()._run_once()

    # ---

    def _process_events(self, *args, **kwargs):
        after_select = self.time()
        self._select_time += after_select - self._before_select

        # print("_process_events", args, kwargs)
        super()._process_events(*args, **kwargs)

        cycle_time = self.time() - self.ref_time
        # self.log.info(f"EVENT {cycle_time}")
        if cycle_time >= self.perf_cycle_time:

            work_time = cycle_time - self._select_time
            self.load = round((work_time/self.perf_cycle_time) * 100.0, 3)
            if self.load > 60:
                self.log.info(f"loop load {self.load}% !!")
            # else:
            #     self.log.info(f"{self.load}%")
            self._select_time = 0
            self.ref_time = self.time()

    # ---