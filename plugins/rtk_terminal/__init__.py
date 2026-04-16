import json
import shlex
from pathlib import Path

RTK_BIN = Path.home() / ".local" / "bin" / "rtk"


def _rtk_available() -> bool:
    return RTK_BIN.exists()


def _wrap_command(command: str) -> str:
    payload = command if command.endswith("\n") else command + "\n"
    escaped = (
        payload.replace("\\", "\\\\")
        .replace("'", "'\"'\"'")
        .replace("\n", "\\n")
    )
    return f"printf '%b' '{escaped}' | {shlex.quote(str(RTK_BIN))} bash"


def _rtk_terminal_handler(args, **kwargs):
    from tools.terminal_tool import terminal_tool

    command = args.get("command", "")
    if not isinstance(command, str) or not command.strip():
        return json.dumps({"error": "command is required"}, ensure_ascii=False)

    return terminal_tool(
        command=_wrap_command(command),
        background=bool(args.get("background", False)),
        timeout=args.get("timeout"),
        task_id=kwargs.get("task_id"),
        workdir=args.get("workdir"),
        pty=bool(args.get("pty", False)),
        notify_on_complete=bool(args.get("notify_on_complete", False)),
        watch_patterns=args.get("watch_patterns"),
    )


def _pre_llm_call(**kwargs):
    return None


def _pre_tool_call(tool_name, args, **kwargs):
    if tool_name != "terminal":
        return None
    return {
        "action": "block",
        "message": (
            "RTK is enabled for this Hermes profile. "
            "Use rtk_terminal instead of terminal unless the user explicitly requests bypassing RTK."
        ),
    }


def register(ctx):
    ctx.register_hook("pre_llm_call", _pre_llm_call)
    ctx.register_hook("pre_tool_call", _pre_tool_call)
    ctx.register_tool(
        name="rtk_terminal",
        toolset="rtk_terminal",
        schema={
            "name": "rtk_terminal",
            "description": "Execute shell commands through RTK by feeding the command to 'rtk bash' via stdin. Accepts the same parameters as terminal.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The shell command to execute through RTK."
                    },
                    "background": {
                        "type": "boolean",
                        "description": "Run the command in the background.",
                        "default": False
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Max seconds to wait in foreground mode.",
                        "minimum": 1
                    },
                    "workdir": {
                        "type": "string",
                        "description": "Working directory for this command."
                    },
                    "pty": {
                        "type": "boolean",
                        "description": "Use a pseudo-terminal for interactive CLI tools.",
                        "default": False
                    },
                    "notify_on_complete": {
                        "type": "boolean",
                        "description": "When background=true, notify when the process exits.",
                        "default": False
                    },
                    "watch_patterns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Background-output patterns that trigger notifications."
                    }
                },
                "required": ["command"]
            }
        },
        handler=_rtk_terminal_handler,
        check_fn=_rtk_available,
        emoji="⚡",
        description="RTK-wrapped terminal execution",
    )
