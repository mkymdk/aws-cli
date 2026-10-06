import threading
import os
import pytest

@pytest.fixture(autouse=True)
def delay_control_s(request, monkeypatch):
    if request.node.name != 'test_open_save_dialog_on_control_s':
        return
    if os.environ.get('OCA_DISABLE_DIALOG'):
        from awscli.autoprompt.widgets import DebugPanelWidget
        monkeypatch.setattr(DebugPanelWidget, '_activate_dialog', lambda self,event: None)
    runner = request.getfixturevalue('app_runner')
    original = runner.app.input.send_text
    timers = []
    def delayed_send(value):
        if value != '\x13':
            return original(value)
        runner._notify_done_rendering(runner.app)
        redraw = threading.Timer(0.05, lambda: runner._notify_done_rendering(runner.app))
        timers.append(redraw)
        redraw.start()
        def deliver():
            if not runner.app.is_done:
                original(value)
        timer = threading.Timer(0.25, deliver)
        timers.append(timer)
        timer.start()
    monkeypatch.setattr(runner.app.input, 'send_text', delayed_send)
    request.addfinalizer(lambda: [timer.join() for timer in timers])
