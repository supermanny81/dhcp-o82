from click.testing import CliRunner

from dhcp_o82 import cli


def test_help():
    runner = CliRunner()
    result = runner.invoke(cli.cli, "")
    assert result.exit_code == 0


def test_inspect():
    runner = CliRunner()
    result = runner.invoke(cli.inspect, "06:0B:31:30:2E:31:2E:31:30:33:2E:34:38")
    assert result.exit_code == 0


def test_create_cid():
    runner = CliRunner()
    result = runner.invoke(cli.create, "-c 548-2-1")
    assert result.exit_code == 0


def test_create_cid_str():
    runner = CliRunner()
    result = runner.invoke(cli.create, "-c mystring")
    assert result.exit_code == 0


def test_create_rid():
    runner = CliRunner()
    result = runner.invoke(cli.create, "-r MY_SWITCH_NAME")
    assert result.exit_code == 0


def test_create_sid():
    runner = CliRunner()
    result = runner.invoke(cli.create, "-s MY_SUB_ID_NAME")
    assert result.exit_code == 0


def test_create_to_hex():
    runner = CliRunner()
    result = runner.invoke(cli.create, "-s MY_SUB_ID_NAME --to-hex")
    assert result.exit_code == 0


def test_create_fail():
    runner = CliRunner()
    result = runner.invoke(cli.create, "")
    assert result.exit_code == 2


def test_create_from():
    runner = CliRunner()
    result = runner.invoke(cli.create_from, "resources/interfaces.csv")
    assert result.exit_code == 0
