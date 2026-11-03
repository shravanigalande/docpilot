from docpilot.accuracy import extract_commands, verify_command


def test_brew_install_restic():
    claim = verify_command(1, "brew install restic", False)
    assert claim.status == "verified"


def test_apt_install_restic():
    claim = verify_command(1, "sudo apt install restic", False)
    assert claim.status == "verified"


def test_apt_get_install_restic():
    claim = verify_command(1, "sudo apt-get install restic", False)
    assert claim.status == "verified"


def test_fake_restic_command_still_fails():
    claim = verify_command(1, "restic fake-command", False)
    assert claim.status == "fail"


def test_extract_installation_commands():
    draft = """```bash
brew install restic
sudo apt install restic
restic snapshots
```"""
    commands = extract_commands(draft)

    assert commands == [
        (2, "brew install restic"),
        (3, "sudo apt install restic"),
        (4, "restic snapshots"),
    ]
