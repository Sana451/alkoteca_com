import time

from .telegram_tools import send_telegram_log, send_file_result


class LoggingTelegramMixin:
    MSG_ENGINE_STARTED = "Started Engine {name} \n {links}"
    MSG_ENGINE_STOPPED = "Stopped Engine \n {name}"
    MSG_SPIDER_ERROR = "Error \n {name}"
    MSG_SPIDER_CLOSED = "Closed {name} \n {reason}"
    MSG_FEED_EXPORTER_CLOSED = "Feed_exporter_closed \n {name}"
    MSG_PROGRESS_UPDATE = "{name} \n обработал {current}/{total} страниц"
    MSG_TIMEOUT_UPDATE = "{name} \n обработал {total_processed} страниц"

    def get_safe(self, attr_name, default=None):
        return getattr(self, attr_name, default)

    def engine_started(self):
        message = self.MSG_ENGINE_STARTED.format(
            name=self.get_safe("name", "unknown"),
            links=self.get_safe('start_url', 'not implemented')
        )
        print(message)
        if self.get_safe("production", False):
            send_telegram_log(message)

    def spider_error(self, spider):
        name = self.get_safe("name")
        log_file = self.get_safe("log_file")
        message = self.MSG_SPIDER_ERROR.format(name=name)
        spider.logger.info(message)
        print(message)
        if self.get_safe("production", False):
            send_telegram_log(message)
            send_file_result(
                file_name=log_file,
                caption=f"Логи \n {name}"
            )

    def spider_closed(self, spider, reason):
        name = self.get_safe("name")
        message = self.MSG_SPIDER_CLOSED.format(name=name, reason=reason)
        results_file_path = self.get_safe("results_file_path")
        spider.logger.info(message)
        print(message)
        if self.get_safe("production"):
            send_telegram_log(message)
            send_file_result(
                file_name=results_file_path,
                caption=f"Результаты \n {name}"
            )

    def feed_exporter_closed(self):
        name = self.get_safe("name")
        results_file_path = self.get_safe("results_file_path")
        message = self.MSG_FEED_EXPORTER_CLOSED.format(name=name)
        print(message)
        if self.get_safe("production"):
            send_telegram_log(message)
            send_file_result(
                file_name=results_file_path,
                caption=f"Результаты \n {name}"
            )


    def engine_stopped(self):
        name = self.get_safe("name")
        message = self.MSG_ENGINE_STOPPED.format(name=name)
        results_file_path = self.get_safe("results_file_path")
        log_file = self.get_safe("log_file")
        print(message)
        if self.get_safe("production"):
            send_telegram_log(message)
            send_file_result(
                file_name=results_file_path,
                caption=f"Результаты \n {name}"
            )
            send_file_result(
                file_name=log_file,
                caption=f"Логи \n {name}"
            )

    def track_progress_for_telegram(self, progress, total):
        name = self.get_safe('name')
        results_file_path = self.get_safe("results_file_path")
        log_file = self.get_safe("log_file")
        progress_checkpoints = self.get_safe("progress_checkpoints", [1, 5, 10, 100, 1000])
        sent_progress_checkpoints = self.get_safe("sent_progress_checkpoints")
        if progress in progress_checkpoints and progress not in sent_progress_checkpoints:
            sent_progress_checkpoints.add(progress)
            message = self.MSG_PROGRESS_UPDATE.format(name=name, current=progress, total=total)
            print(message)
            if self.get_safe("production"):
                send_telegram_log(message)
                send_file_result(
                    file_name=results_file_path,
                    caption=f"Промежуточные результаты \n {name}"
                )
                send_file_result(
                    file_name=log_file,
                    caption=f"Логи \n {name}"
                )

    def send_updates_with_timeout(self):
        name = self.get_safe('name')
        results_file_path = self.get_safe("results_file_path")
        log_file = self.get_safe("log_file")
        last_sent_time = self.get_safe("last_sent_time")
        send_interval = self.get_safe("send_interval")

        if send_interval:
            # Проверка, прошло ли достаточно времени с последней отправки
            current_time = time.time()
            total_processed = self.crawler.stats.get_value('scheduler/dequeued')
            if current_time - last_sent_time >= send_interval:
                message = self.MSG_TIMEOUT_UPDATE.format(name=name, total_processed=total_processed)
                print(message)

                if self.get_safe("production"):
                    send_telegram_log(message)
                    send_file_result(
                        file_name=results_file_path,
                        caption=f"Промежуточные результаты \n {name}"
                    )
                    send_file_result(
                        file_name=log_file,
                        caption=f"Логи \n {name}"
                    )

                self.last_sent_time = current_time
