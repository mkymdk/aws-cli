import time
import os
import threading
import pytest
@pytest.fixture(autouse=True)
def delay_initialization(request,monkeypatch):
    if request.node.name != 'test_handle_args_with_spaces':
        return
    runner=request.getfixturevalue('app_runner')
    prompter=request.getfixturevalue('prompter')
    original=prompter._set_input_buffer_text
    def delayed(value):
        runner._notify_done_rendering(runner.app)
        redraw=threading.Timer(0.05,lambda: runner._notify_done_rendering(runner.app))
        redraw.start()
        time.sleep(0.25)
        redraw.join()
        if not os.environ.get('OCA_SKIP_FINALIZATION'):
            return original(value)
    monkeypatch.setattr(prompter,'_set_input_buffer_text',delayed)
