from app.utils.files import sanitize_filename


def test_sanitize_filename_basics():
    assert sanitize_filename("test.txt") == "test.txt"
    assert sanitize_filename("My File.mp3") == "My_File.mp3"
    assert sanitize_filename(None) == "unnamed_file"
    assert sanitize_filename("") == "unnamed_file"


def test_sanitize_filename_traversal():
    # ../ patterns
    assert sanitize_filename("../../etc/passwd") == "passwd"
    assert (
        sanitize_filename("..") == "unnamed_file"
    )  # basename of ".." is empty or ".." depending on os.path, but my regex handles it

    # Check what os.path.basename("..") does:
    # On linux it returns "..".
    # sanitize_filename("..") -> basename ".." -> replace dots?
    # My regex is [^a-zA-Z0-9._-] replaced by _.
    # So ".." stays "..".
    # But then I do strip(". ").
    # So ".." -> "". -> "unnamed_file".
    # Let's verify this logic in test.

    assert sanitize_filename("../foo/bar") == "bar"
    assert sanitize_filename("/absolute/path/to/file") == "file"


def test_sanitize_filename_dangerous_chars():
    assert sanitize_filename("file;rm -rf /") == "unnamed_file"
    assert sanitize_filename("$(whoami).txt") == "__whoami_.txt"
    assert sanitize_filename("<script>.js") == "_script_.js"


def test_sanitize_filename_reserved_names():
    # Windows reserved names
    assert sanitize_filename("CON.txt") == "_CON.txt"
    assert sanitize_filename("aux") == "_aux"


def test_sanitize_filename_unicode():
    assert sanitize_filename("café.txt") == "cafe.txt"


if __name__ == "__main__":
    try:
        test_sanitize_filename_basics()
        test_sanitize_filename_traversal()
        test_sanitize_filename_dangerous_chars()
        test_sanitize_filename_reserved_names()
        test_sanitize_filename_unicode()
        print("All tests passed!")
    except AssertionError as e:
        print(f"Test failed: {e}")
        exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)
