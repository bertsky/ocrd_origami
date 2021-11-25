import click

from ocrd.decorators import ocrd_cli_options, ocrd_cli_wrap_processor
from .segment import OcrdOrigamiSegment

@click.command()
@ocrd_cli_options
def ocrd_origami_segment(*args, **kwargs):
    return ocrd_cli_wrap_processor(OcrdOrigamiSegment, *args, **kwargs)
