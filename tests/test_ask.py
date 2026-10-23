import sys
from types import SimpleNamespace

import app.ask as ask_module


def test_main_keeps_one_chat_for_multiple_questions(monkeypatch, capsys):
    class FakeChat:
        def __init__(self):
            self.questions = []

        def send_message(self, question):
            self.questions.append(question)
            return SimpleNamespace(text=f"answer: {question}", usage_metadata=None)

    chat = FakeChat()
    create_calls = []

    class FakeClient:
        class Chats:
            def create(self, *, model):
                create_calls.append(model)
                return chat

        chats = Chats()

    monkeypatch.setattr(ask_module.genai, "Client", lambda api_key: FakeClient())
    monkeypatch.setattr(sys, "argv", ["app.ask"])
    questions = iter(["first question", "follow-up", "exit"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(questions))

    ask_module.main()

    assert chat.questions == ["first question", "follow-up"]
    assert create_calls == [ask_module.MODEL]
    assert "answer: first question" in capsys.readouterr().out
