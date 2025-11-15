from src.security.masking import mask_text, safe_note_len


def test_mask_text_basic():
    assert mask_text("Secret") == "Se****"
    assert mask_text("Hi") == "Hi"
    assert mask_text("") == ""
    assert mask_text(None) == ""


def test_safe_note_len():
    assert safe_note_len("abc") == 3
    assert safe_note_len("") == 0
    assert safe_note_len(None) == 0
