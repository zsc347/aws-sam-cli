"""
CLI command for "local start-lambda" command
"""

import logging
import click

from samcli.cli.main import pass_context, common_options as cli_framework_options
from samcli.commands.local.cli_common.options import invoke_common_options, service_common_options
from samcli.commands.local.cli_common.invoke_context import InvokeContext
from samcli.commands.local.cli_common.user_exceptions import UserException
from samcli.commands.local.lib.local_lambda_service import LocalLambdaService
from samcli.commands.validate.lib.exceptions import InvalidSamDocumentException

LOG = logging.getLogger(__name__)

HELP_TEXT = """
Allows you to run a Local Lambda Service that will service the invoke path to your functions for quick development &
 testing through the AWS CLI or SDKs. When run in a directory that contains your Serverless functions and your AWS
 SAM template, it will create a local HTTP server that wil response to the invoke call to your functions.
 When accessed (via browser, cli etc), it will launch a Docker container locally to invoke the function. It will read
 the CodeUri property of AWS::Serverless::Function resource to find the path in your file system containing the Lambda
 Function code. This could be the project's root directory for interpreted languages like Node & Python, or a build
 directory that stores your compiled artifacts or a JAR file. If you are using a interpreted language, local changes
 will be available immediately in Docker container on every invoke. For more compiled languages or projects requiring
 complex packing support, we recommended you run your own building solution and point SAM to the directory or file
 containing build artifacts.
"""


@click.command("start-lambda", help=HELP_TEXT, short_help="Runs a Local Lambda Service (for the Invoke path only)")
@service_common_options(3001)
@invoke_common_options
@cli_framework_options
@pass_context
def cli(ctx,
        # start-lambda Specific Options
        host, port,

        # Common Options for Lambda Invoke
        template, env_vars, debug_port, debug_args, docker_volume_basedir,
        docker_network, log_file, skip_pull_image, profile
        ):
    # All logic must be implemented in the ``do_cli`` method. This helps with easy unit testing

    do_cli(ctx, host, port, template, env_vars, debug_port, debug_args, docker_volume_basedir,
           docker_network, log_file, skip_pull_image, profile)  # pragma: no cover


def do_cli(ctx, host, port, template, env_vars, debug_port, debug_args,  # pylint: disable=R0914
           docker_volume_basedir, docker_network, log_file, skip_pull_image, profile):
    """
    Implementation of the ``cli`` method, just separated out for unit testing purposes
    """

    LOG.debug("local start_lambda command is called")

    # Pass all inputs to setup necessary context to invoke function locally.
    # Handler exception raised by the processor for invalid args and print errors

    try:
        with InvokeContext(template_file=template,
                           function_identifier=None,  # Don't scope to one particular function
                           env_vars_file=env_vars,
                           debug_port=debug_port,
                           debug_args=debug_args,
                           docker_volume_basedir=docker_volume_basedir,
                           docker_network=docker_network,
                           log_file=log_file,
                           skip_pull_image=skip_pull_image,
                           aws_profile=profile) as invoke_context:

            service = LocalLambdaService(lambda_invoke_context=invoke_context,
                                         port=port,
                                         host=host)
            service.start()

    except InvalidSamDocumentException as ex:
        raise UserException(str(ex))
