#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

import difflib
import inspect
import logging

from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.types import Message

from .. import loader, security, utils

logger = logging.getLogger(__name__)


@loader.tds
class HelpMod(loader.Module):
    """Help module, made specifically for Hikka with <3"""

    strings = {
        "name": "Help",
        "bad_module": "<b>🚫 <b>Module</b> <code>{}</code> <b>not found</b>",
        "single_mod_header": "🌑 <b>{}</b>:",
        "single_cmd": "\n▫️ <code>{}{}</code> {}",
        "undoc_cmd": "🦥 No docs",
        "all_header": "🌘 <b>{} mods available, {} hidden:</b>",
        "mod_tmpl": "\n{} <code>{}</code>",
        "first_cmd_tmpl": ": ( {}",
        "cmd_tmpl": " | {}",
        "no_mod": "🚫 <b>Specify module to hide</b>",
        "hidden_shown": "🌘 <b>{} modules hidden, {} modules shown:</b>\n{}\n{}",
        "ihandler": "\n🎹 <code>{}</code> {}",
        "undoc_ihandler": "🦥 No docs",
        "joined": (
            "🌘 <b>Joined the</b> <a href='https://t.me/hikka_talks'>support chat</a>"
        ),
        "join": "🌘 <b>Join the</b> <a href='https://t.me/hikka_talks'>support chat</a>",
        "partial_load": (
            "⚠️ <b>Userbot is not fully loaded, so not all modules are shown</b>"
        ),
        "not_exact": (
            "⚠️ <b>No exact match occured, so the closest result is shown instead</b>"
        ),
    }

    strings_ru = {
        "bad_module": "<b>🚫 <b>Модуль</b> <code>{}</code> <b>не найден</b>",
        "single_mod_header": "🌑 <b>{}</b>:",
        "single_cmd": "\n▫️ <code>{}{}</code> {}",
        "undoc_cmd": "🦥 Нет описания",
        "all_header": "🌘 <b>{} модулей доступно, {} скрыто:</b>",
        "mod_tmpl": "\n{} <code>{}</code>",
        "first_cmd_tmpl": ": ( {}",
        "cmd_tmpl": " | {}",
        "no_mod": "🚫 <b>Укажи модуль(-и), которые нужно скрыть</b>",
        "hidden_shown": "🌘 <b>{} модулей скрыто, {} модулей показано:</b>\n{}\n{}",
        "ihandler": "\n🎹 <code>{}</code> {}",
        "undoc_ihandler": "🦥 Нет описания",
        "joined": (
            "🌘 <b>Вступил в</b> <a href='https://t.me/hikka_talks'>чат помощи</a>"
        ),
        "join": "🌘 <b>Вступи в</b> <a href='https://t.me/hikka_talks'>чат помощи</a>",
        "_cmd_doc_helphide": (
            "<модуль(-и)> - Скрывает модуль(-и) из помощи\n*Разделяй имена модулей"
            " пробелами"
        ),
        "_cmd_doc_help": "[модуль] [-f] - Показывает помощь",
        "_cmd_doc_support": "Вступает в чат помощи Hikka",
        "_cls_doc": "Модуль помощи, сделанный специально для Hikka <3",
        "partial_load": (
            "⚠️ <b>Юзербот еще не загрузился полностью, поэтому показаны не все"
            " модули</b>"
        ),
        "not_exact": (
            "⚠️ <b>Точного совпадения не нашлось, поэтому было выбрано наиболее"
            " подходящее</b>"
        ),
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "core_emoji",
                "▪️",
                lambda: "Core module bullet",
                validator=loader.validators.String(length=1),
            ),
            loader.ConfigValue(
                "hikka_emoji",
                "🌘",
                lambda: "Hikka-only module bullet",
                validator=loader.validators.String(length=1),
            ),
            loader.ConfigValue(
                "plain_emoji",
                "▫️",
                lambda: "Plain module bullet",
                validator=loader.validators.String(length=1),
            ),
            loader.ConfigValue(
                "empty_emoji",
                "👁‍🗨",
                lambda: "Empty modules bullet",
                validator=loader.validators.String(length=1),
            ),
        )

    async def helphidecmd(self, message: Message):
        """<module or modules> - Hide module(-s) from help
        *Split modules by spaces"""
        modules = utils.get_args(message)
        if not modules:
            await utils.answer(message, self.strings("no_mod"))
            return

        mods = [
            i.strings["name"]
            for i in self.allmodules.modules
            if hasattr(i, "strings") and "name" in i.strings
        ]

        modules = list(filter(lambda module: module in mods, modules))
        currently_hidden = self.get("hide", [])
        hidden, shown = [], []
        for module in modules:
            if module in currently_hidden:
                currently_hidden.remove(module)
                shown += [module]
            else:
                currently_hidden += [module]
                hidden += [module]

        self.set("hide", currently_hidden)

        await utils.answer(
            message,
            self.strings("hidden_shown").format(
                len(hidden),
                len(shown),
                "\n".join([f"👁‍🗨 <i>{m}</i>" for m in hidden]),
                "\n".join([f"👁 <i>{m}</i>" for m in shown]),
            ),
        )

    async def modhelp(self, message: Message, args: str):
        exact = True
        module = self.lookup(args)

        if not module:
            _args = args.lower()
            _args = _args[1:] if _args.startswith(self.get_prefix()) else _args
            if _args in self.allmodules.commands:
                module = self.allmodules.commands[_args].__self__

        if not module:
            module = self.lookup(
                next(
                    (
                        reversed(
                            sorted(
                                [
                                    module.strings["name"]
                                    for module in self.allmodules.modules
                                ],
                                key=lambda x: difflib.SequenceMatcher(
                                    None,
                                    args.lower(),
                                    x,
                                ).ratio(),
                            )
                        )
                    ),
                    None,
                )
            )

            exact = False

        try:
            name = module.strings("name")
        except KeyError:
            name = getattr(module, "name", "ERROR")

        _name = (
            f"{utils.escape_html(name)} (v{module.__version__[0]}.{module.__version__[1]}.{module.__version__[2]})"
            if hasattr(module, "__version__")
            else utils.escape_html(name)
        )

        reply = self.strings("single_mod_header").format(_name)
        if module.__doc__:
            reply += "<i>\nℹ️ " + utils.escape_html(inspect.getdoc(module)) + "\n</i>"

        commands = {
            name: func
            for name, func in module.commands.items()
            if await self.allmodules.check_security(message, func)
        }

        if hasattr(module, "inline_handlers"):
            for name, fun in module.inline_handlers.items():
                reply += self.strings("ihandler").format(
                    f"@{self.inline.bot_username} {name}",
                    (
                        utils.escape_html(inspect.getdoc(fun))
                        if fun.__doc__
                        else self.strings("undoc_ihandler")
                    ),
                )

        for name, fun in commands.items():
            reply += self.strings("single_cmd").format(
                self.get_prefix(),
                name,
                (
                    utils.escape_html(inspect.getdoc(fun))
                    if fun.__doc__
                    else self.strings("undoc_cmd")
                ),
            )

        await utils.answer(
            message, f"{reply}\n\n{'' if exact else self.strings('not_exact')}"
        )

    @loader.unrestricted
    async def helpcmd(self, message: Message):
        """[module] [-f] - Show help"""
        args = utils.get_args_raw(message)
        force = False
        if "-f" in args:
            args = args.replace(" -f", "").replace("-f", "")
            force = True

        if args:
            await self.modhelp(message, args)
            return

        count = 0
        for i in self.allmodules.modules:
            try:
                if i.commands or i.inline_handlers:
                    count += 1
            except Exception:
                pass

        hidden = self.get("hide", [])

        reply = self.strings("all_header").format(count, 0 if force else len(hidden))
        shown_warn = False

        plain_ = []
        core_ = []
        inline_ = []
        no_commands_ = []

        for mod in self.allmodules.modules:
            if not hasattr(mod, "commands"):
                logger.debug(f"Module {mod.__class__.__name__} is not inited yet")
                continue

            if mod.strings["name"] in self.get("hide", []) and not force:
                continue

            tmp = ""

            try:
                name = mod.strings["name"]
            except KeyError:
                name = getattr(mod, "name", "ERROR")

            inline = (
                hasattr(mod, "callback_handlers")
                and mod.callback_handlers
                or hasattr(mod, "inline_handlers")
                and mod.inline_handlers
            )

            if not inline:
                for cmd_ in mod.commands.values():
                    try:
                        inline = "await self.inline.form(" in inspect.getsource(
                            cmd_.__code__
                        )
                    except Exception:
                        pass

            core = mod.__origin__ == "<core>"

            if core:
                emoji = self.config["core_emoji"]
            elif inline:
                emoji = self.config["hikka_emoji"]
            else:
                emoji = self.config["plain_emoji"]

            if (
                not getattr(mod, "commands", None)
                and not getattr(mod, "inline_handlers", None)
                and not getattr(mod, "callback_handlers", None)
            ):
                no_commands_ += [
                    self.strings("mod_tmpl").format(self.config["empty_emoji"], name)
                ]
                continue

            tmp += self.strings("mod_tmpl").format(emoji, name)
            first = True

            commands = [
                name
                for name, func in mod.commands.items()
                if await self.allmodules.check_security(message, func) or force
            ]

            for cmd in commands:
                if first:
                    tmp += self.strings("first_cmd_tmpl").format(cmd)
                    first = False
                else:
                    tmp += self.strings("cmd_tmpl").format(cmd)

            icommands = [
                name
                for name, func in mod.inline_handlers.items()
                if await self.inline.check_inline_security(
                    func=func,
                    user=message.sender_id,
                )
                or force
            ]

            for cmd in icommands:
                if first:
                    tmp += self.strings("first_cmd_tmpl").format(f"🎹 {cmd}")
                    first = False
                else:
                    tmp += self.strings("cmd_tmpl").format(f"🎹 {cmd}")

            if commands or icommands:
                tmp += " )"
                if core:
                    core_ += [tmp]
                elif inline:
                    inline_ += [tmp]
                else:
                    plain_ += [tmp]
            elif not shown_warn and (mod.commands or mod.inline_handlers):
                reply = (
                    "<i>You have permissions to execute only these"
                    f" commands</i>\n{reply}"
                )
                shown_warn = True

        plain_.sort(key=lambda x: x.split()[1])
        core_.sort(key=lambda x: x.split()[1])
        inline_.sort(key=lambda x: x.split()[1])
        no_commands_.sort(key=lambda x: x.split()[1])
        no_commands_ = "".join(no_commands_) if force else ""

        partial_load = (
            ""
            if self.lookup("Loader")._fully_loaded
            else f"\n\n{self.strings('partial_load')}"
        )

        await utils.answer(
            message,
            f"{reply}\n{''.join(core_)}{''.join(plain_)}{''.join(inline_)}{no_commands_}{partial_load}",
        )

    async def supportcmd(self, message):
        """Joins the support Hikka chat"""
        if await self.allmodules.check_security(
            message,
            security.OWNER | security.SUDO,
        ):
            await self._client(JoinChannelRequest("https://t.me/hikka_talks"))

            try:
                await self.inline.form(
                    self.strings("joined"),
                    reply_markup=[
                        [{"text": "👩‍💼 Chat", "url": "https://t.me/hikka_talks"}]
                    ],
                    ttl=10,
                    message=message,
                )
            except Exception:
                await utils.answer(message, self.strings("joined"))
        else:
            try:
                await self.inline.form(
                    self.strings("join"),
                    reply_markup=[
                        [{"text": "👩‍💼 Chat", "url": "https://t.me/hikka_talks"}]
                    ],
                    ttl=10,
                    message=message,
                )
            except Exception:
                await utils.answer(message, self.strings("join"))
