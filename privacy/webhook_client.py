import asyncio
import json


from pydantic import ValidationError
from starlette.concurrency import run_in_threadpool
import responder


from privacy.schema.transaction import Transaction
from privacy.util.logging import LoggingClass


class WebhookClient(LoggingClass):
    hmac_strict = True

    def __init__(self, *handlers):
        self.api = responder.API()  # cors_params=dict(allow_methods=("POST", )))
        self.handlers = handlers or []
        self.api.add_route("/", self.listener)

    async def listener(self, req, resp):
        # TODO: return error messages.
        # TODO: Logging
        if False and self.hmac_strict:
            resp.status_code = 406  # TODO: what actually fits here.
            return

        #  TODO: actually be secure
    #    if not req.is_secure:
            # TODO: Drop instead of redirecting.
    #        resp.status_code = 301   # TODO: same here
    #        resp.headers["Location"] = "https://127.0.0.1/"
    #        return

        if req.mimetype != "application/json":
            resp.status_code = 415
            return

        data = await req.media("json")
        try:
            transaction = Transaction(**data)
        except ValidationError as e:
            print(dir(e))
            print(e.errors)
            print(e.raw_errors)
            resp.status_code = 412
            resp.content = json.dumps({"errors": str(e)})  # TODO: actually handle the error message.
            resp.headers["Content-Type"] = "application/json"
            return

        for handler in self.handlers:
            try:
                if asyncio.iscoroutinefunction(handler) or asyncio.iscoroutinefunction(handler.__call__):
                    await handler(self, transaction)
                else:
                    await run_in_threadpool(handler, transaction)
            except Exception as e:
                self.log.exception(
                    "Webhook handler %s raise exception %s: %s",
                    handler.__name__, e.__class__.__name__, e)

        resp.status_code = 204

    def run(self):
        self.api.run()

    @classmethod
    # TODO: this
    def spawn_in_thread(cls):
        pass

# client = WebhookClient()
# client.run()
