from dhcp_o82.o82 import Option82, SubOptFormat


def test_mac_formats():
    hex = "01:06:00:04:02:24:02:01:02:08:00:06:4C:71:0C:45:63:00"
    assert Option82((548, 2, 1), "4c71.0c45.6300").to_hex() == hex
    assert Option82((548, 2, 1), "4c710c456300").to_hex() == hex
    assert Option82((548, 2, 1), "4c:71:0c:45:63:00").to_hex() == hex


def test_get_cid():
    cid = Option82.from_hex(
        "01:06:00:04:02:24:02:06:02:08:00:06:4C:71:0C:45:63:00"
    ).get_circuit_id(SubOptFormat.CIRCUIT_ID)
    assert cid == "548-2-6"


def test_get_cid_hex():
    cid = Option82.from_hex(
        "01:06:00:04:02:24:02:06:02:08:00:06:4C:71:0C:45:63:00"
    ).get_circuit_id(SubOptFormat.HEX)
    assert cid == "02:24:02:06"


def test_get_cid_string():
    cid = Option82.from_hex(
        "01:19:00:17:54:77:6F:47:69:67:61:62:69:74:45:74:68:65:72:6E:65:74:32:2F:30:2F:36:02:12:00:10:73:76:6C:67:6F:6C:64:33:31:2D:6F:74:2D:73:77:31"
    ).get_circuit_id(SubOptFormat.STRING)
    assert cid == "TwoGigabitEthernet2/0/6"


def test_get_rid():
    rid = Option82.from_hex(
        "01:19:00:17:54:77:6F:47:69:67:61:62:69:74:45:74:68:65:72:6E:65:74:32:2F:30:2F:36:02:12:00:10:73:76:6C:67:6F:6C:64:33:31:2D:6F:74:2D:73:77:31"
    ).get_remote_id()
    assert rid == "73:76:6c:67:6f:6c:64:33:31:2d:6f:74:2d:73:77:31"


def test_get_rid_string():
    rid = Option82.from_hex(
        "01:19:00:17:54:77:6F:47:69:67:61:62:69:74:45:74:68:65:72:6E:65:74:32:2F:30:2F:36:02:12:00:10:73:76:6C:67:6F:6C:64:33:31:2D:6F:74:2D:73:77:31"
    ).get_remote_id(SubOptFormat.STRING)
    assert rid == "svlgold31-ot-sw1"


def test_sub_id():
    sid = Option82(None, None, "SID").to_hex()
    assert sid == "06:03:53:49:44"


def test_sub_id_str():
    val = "SOME-RANDOM_STRING FOR TESTING"
    sid = Option82(None, None, val).get_subscriber_id(SubOptFormat.STRING)
    assert sid == val


def test_str():
    expected = """06:0B:31:30:2E:31:2E:31:30:33:2E:34:38

sub-option: 6 (0x6), name: SUBSCRIBER_ID, length: 11 (0xb)
  val: 31:30:2e:31:2e:31:30:33:2e:34:38
  string: 10.1.103.48

"""
    out = str(Option82.from_hex("06:0B:31:30:2E:31:2E:31:30:33:2E:34:38"))
    assert expected == out


def test_csv():
    Option82.from_csv("resources/interfaces.csv", "resources/interfaces-modified.csv")
