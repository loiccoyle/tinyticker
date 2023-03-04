from unittest import TestCase

from tinyticker.web import command


class TestCommand(TestCase):
    def test_register(self):
        assert "new" not in command.COMMANDS.keys()

        @command.register
        def new():
            """Test command"""
            pass

        assert "new" in command.COMMANDS.keys()
        assert command.COMMANDS["new"].func == new
        assert command.COMMANDS["new"].desc == "Test command"

    def test_try_command(self):
        command.try_command("echo test")
        command.try_command(["echo test"])
        command.try_command("somecommandwhichdoesnotexist")
