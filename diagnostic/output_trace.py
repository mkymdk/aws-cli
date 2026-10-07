import json
import os
import threading
import time
from pathlib import Path
import tests
from prompt_toolkit.keys import Keys


def pytest_configure(config):
    original = tests.PromptToolkitAppRunner.feed_input
    def feed(self, *keys):
        path = Path(os.environ['TRACE_FILE'])
        def record(kind, **extra):
            data = dict(time=time.monotonic(), event=kind,
                        thread=threading.current_thread().name,
                        keys=[str(k) for k in keys],
                        show_output=self.app.show_output,
                        show_doc=self.app.show_doc, **extra)
            with path.open('a') as f:
                f.write(json.dumps(data) + '\n')
        if not getattr(self, '_output_trace_attached', False):
            self._output_trace_attached = True
            self.app.key_processor.before_key_press.add_handler(
                lambda sender: record('before_key'))
            self.app.key_processor.after_key_press.add_handler(
                lambda sender: record('after_key'))
            self.app.after_render.add_handler(lambda sender: record('render'))
        send = self.app.input.send_text
        timer = None
        mode = os.environ.get('TRACE_MODE', 'natural')
        def delayed(text):
            nonlocal timer
            record('queued_input')
            def deliver():
                record('delivered_input')
                send(text)
            timer = threading.Timer(0.5, deliver)
            timer.start()
            self._done_rendering_event.set()
        if mode == 'controlled' and keys == (Keys.F5,):
            self.app.input.send_text = delayed
        record('feed_start')
        try:
            return original(self, *keys)
        finally:
            record('feed_return')
            self.app.input.send_text = send
    tests.PromptToolkitAppRunner.feed_input = feed


def pytest_runtest_call(item):
    if os.environ.get('TRACE_MODE') == 'broken':
        runner = item.funcargs.get('app_runner')
        if runner:
            for binding in runner.app.key_bindings.get_bindings_for_keys((Keys.F5,)):
                binding.handler = lambda event: None
