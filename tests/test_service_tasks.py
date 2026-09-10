import time

from ra_common.envelope import Envelope
from ra_common.messaging import Command, CommandMessage
from ra_common.service import Service, ServiceCore, ServiceReport, ServiceStatus
from ra_common.tasks import RunnerStatus, Task, TaskConfig, TaskRunner


class Toy(Service):
    def __init__(self) -> None:
        self.core = ServiceCore("ra.test.Toy")
        self.started = False

    def start(self, properties):
        self.started = True
        self.core.update_status(ServiceStatus.RUNNING)
        return True

    def shutdown(self):
        self.started = False
        self.core.update_status(ServiceStatus.SHUTDOWN)
        return True


def test_command_message_drives_lifecycle():
    toy = Toy()
    e = Envelope.command()
    e.message = CommandMessage(Command.START)
    toy.handle(e)
    assert toy.started
    assert toy.service_status() is ServiceStatus.RUNNING

    r = Envelope.command()
    r.message = CommandMessage(Command.REPORT)
    toy.handle(r)
    assert r.header("result") is not None


def test_report_round_trip():
    rep = ServiceReport("ra.http.HttpService", ServiceStatus.RUNNING, registered=True, running=True, version="0.1.0")
    back = ServiceReport.from_dict(rep.to_dict())
    assert back.service_status is ServiceStatus.RUNNING
    assert back.running


class Counter(Task):
    def __init__(self, cfg: TaskConfig) -> None:
        self._cfg = cfg
        self.runs = 0

    def config(self):
        return self._cfg

    def execute(self):
        self.runs += 1
        return True


def test_one_shot_runs_once_and_is_reaped():
    runner = TaskRunner()
    runner.set_poll_period_ms(20)
    task = Counter(TaskConfig.once("c"))
    runner.add_task(task)
    runner.start()
    for _ in range(100):
        if task.runs >= 1 and runner.task_count() == 0:
            break
        time.sleep(0.01)
    assert task.runs == 1
    assert runner.task_count() == 0
    runner.shutdown()
    assert runner.status() is RunnerStatus.SHUTDOWN


def test_periodic_runs_multiple_times():
    runner = TaskRunner()
    runner.set_poll_period_ms(10)
    task = Counter(TaskConfig.periodic("p", 10))
    runner.add_task(task)
    runner.start()
    time.sleep(0.15)
    runner.shutdown()
    assert task.runs >= 2
