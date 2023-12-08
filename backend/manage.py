import typing
import sys

import uvicorn
import alembic

alembic.context

# "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"
try:
    from app.main import app
except ImportError as exc:
    raise ImportError("Couldn't import FastApi Instance.")


def start_server(options: typing.List[str]) -> None:
    host, port = options if options else [ "0.0.0.0", "8000" ]
    port = int(port)

    uvicorn.run("manage:app", host=host, port=port, reload=True)
    

action_map = {
    "start_server": start_server,
}

if __name__ == "__main__":
    args = sys.argv[1:]
    action = args[0]
    options = args[1:]
    try:
        action_map[action](options)
    except Exception as exc:
        print(exc)
        raise exc