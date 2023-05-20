#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Run this script before submitting to git.

This preforms a number of check and normalization functions, including
 - reuse
 - lint
 - test
The aim is to make sure the code is fully tested and ready to be submitted to git.
All tools which should be run before submission will be run.
This script is intended to be run locally.
"""

# store the status for EVERY tool run. Not just the latest.
# currently need to invoke the python tools from the root of the repo - is this good?

import logging

from mewbot.tools import gather_paths
from mewbot.tools.lint import LintToolchain
from mewbot.tools.reuse import ReuseToolchain
from mewbot.tools.test import TestToolchain
from mewbot.tools.terminal import CommandDelimiter, ResultPrinter


class PreflightToolChain:
    """
    Class to run the tools in sequence.
    """

    _logger: logging.Logger

    # Does your code pass muster?
    preflight_okay: bool = False

    reuse_success: bool
    lint_success: dict[str, bool]
    test_success: bool

    def __init__(self) -> None:
        """Startup preflight - define the logger."""

        self._logger = logging.Logger("preflight tool run")
        self._logger.setLevel(logging.INFO)

    def run(self) -> None:
        """
        Run all needed tools in sequence.

        Reuse - Will be run against the current position.
        :return:
        """
        self.run_reuse()
        self.run_lint()
        self.run_test()

        ResultPrinter(
            {"Reuse result": self.reuse_success, "Tests result": self.test_success},
            self.lint_success,
        ).result_print()

    def run_reuse(self) -> None:
        """
        Run the reuse tool and store the result.

        :return:
        """
        # reuse
        self._logger.info("Starting reuse run")
        with CommandDelimiter("Starting reuse run"):
            reuse_tool = ReuseToolchain(".", in_ci=False)

            print("Running reuse")

            for _ in reuse_tool.run():
                ...

            self.reuse_success = reuse_tool.success

    def run_lint(self) -> None:
        """
        Run the lint toolchain and store the result.

        :return:
        """
        self._logger.info("Starting linting run")

        with CommandDelimiter("Starting linting run"):
            target_paths = gather_paths("src", "tests")
            paths = list(target_paths)

            print(f"Running lint on {paths}")

            linter = LintToolchain(*paths, in_ci=False)
            for _ in linter.run():
                ...

            self.lint_success = linter.run_success

    def run_test(self) -> None:
        """Run the test suite - store the results."""
        self._logger.info("Starting the testing run")

        paths = list(gather_paths("tests"))
        tester = TestToolchain(*paths, in_ci=False)
        with CommandDelimiter("Starting testing run"):
            print(f"Running tests on {paths}")

            for _ in tester.run():
                ...

        self.test_success = tester.success


if __name__ == "__main__":
    preflight_toolchain = PreflightToolChain()
    preflight_toolchain.run()
