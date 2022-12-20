import re

import click

from dhcp_o82.o82 import Option82


@click.group()
def cli():
    """
    Makes humans working with DHCP Option 82/RelayAgentInfo possible.

    Decodes or encodes sub options in DHCP Option 82 packets for
    troubleshooting or making lease reservations on a DHCP server.
    """
    pass


@click.command()
@click.argument("hex")
def inspect(hex):
    """Decode hex value and show sub option details.

    Returns a breakdown of hex contents.

    \b
    06:0B:31:30:2E:31:2E:31:30:33:2E:34:38

    \b
    sub-option: 6 (0x6), name: SUBSCRIBER_ID, length: 11 (0xb)
        val: 31:30:2e:31:2e:31:30:33:2e:34:38
        string: 10.1.103.48
    """
    click.echo(Option82.from_hex(hex))


@click.command()
@click.option(
    "--circuit-id",
    "-c",
    required=False,
    default=None,
    help="String value of a circuit id use the following format. "
    "vlan-module-port example: 548-1-6",
)
@click.option(
    "--remote-id",
    "-r",
    required=False,
    default=None,
    help="String or MAC address for remote id.",
)
@click.option(
    "--subscriber-id",
    "-s",
    required=False,
    default=None,
    help="A string value to use for subscriber id.",
)
@click.option(
    "--to-hex", is_flag=True, required=False, help=("Display only hex value.")
)
def create(circuit_id: str, remote_id: str, subscriber_id: str, to_hex: bool):
    """Creates lookup key (hex) for the supplied sub options."""
    if any([circuit_id, remote_id, subscriber_id]):
        o82 = Option82()
        if circuit_id:
            match = re.match(
                r"(?P<vlan>\d*)\-(?P<module>\d*)\-(?P<port>\d*)", circuit_id
            )
            if match:
                vals = match.groupdict()
                o82.set_circuit_id(
                    (int(vals["vlan"]), int(vals["module"]), int(vals["port"]))
                )
            else:
                o82.set_circuit_id(circuit_id)
        if remote_id:
            o82.set_remote_id(remote_id)
        if subscriber_id:
            o82.set_subscriber_id(subscriber_id)

        if to_hex:
            click.echo(o82.to_hex())
        else:
            click.echo(o82)
    else:
        raise click.UsageError(
            (
                "At least one option (circuit, remote, or subscriber id)"
                " must be passed."
            )
        )


@click.command()
@click.argument("file_in")
@click.argument("file_out", required=False)
def create_from(file_in, file_out=None):
    """Process a csv document and append hex lookup keys to a new file.

    Uses the following fields to generate the hex for an option 82 packet.
    At least one of these sub options must exist.

    \b
    circuit_id - string or use vlan, module, and port - all int
    remote_id - A string or mac address
    subscriber_id - string value

    \b
    Example:
        vlan,module,port,remote_id
        548,1,1,switch1
        548,1,4,switch1
        548,1,7,switch1
    """
    if file_out is None:
        basename = file_in.removesuffix(".csv")
        file_out = f"{basename}-modified.csv"
    Option82.from_csv(file_in, file_out)


cli.add_command(inspect)
cli.add_command(create)
cli.add_command(create_from)

if __name__ == "__main__":
    cli()
