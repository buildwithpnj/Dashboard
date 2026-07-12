import pytest
from app.security.spam_pattern_detector import SpamPatternDetector

def test_spam_pattern_detection():
    # Normal query
    assert not SpamPatternDetector.is_spam("correct grammar: I went home")

    # Repetitive characters spam
    assert SpamPatternDetector.is_spam("aaaaaaaaaaaaaaaaaaa")

    # Repetitive word loop spam
    assert SpamPatternDetector.is_spam("spam spam spam spam spam spam spam spam spam spam spam")
