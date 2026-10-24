# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)
#
# Local override: pin a real taskflow release that supports C++17.
# The builtin recipe only lists `master`, which moved to C++20 (v4.x API);
# deal.II 9.7 is built with cxxstd=17 and requires taskflow@3.10:.

from spack_repo.builtin.packages.taskflow.package import Taskflow as BuiltinTaskflow

from spack.package import *


class Taskflow(BuiltinTaskflow):
    """Taskflow pinned to the latest v3 release (C++17 compatible) to satisfy
    deal.II's taskflow@3.10: requirement without pulling the C++20 `master`."""

    # v3.11.0 (2024-05): requires C++17, release id 3.10: satisfies
    version("3.11.0", sha256="5e45a7ee032cae136843c76824519acbc0306f02d682f7e69fb1d53f69173dcb")
    # v3.10.0 (2024-02): C++17 compatible release
    version("3.10.0", sha256="fe86765da417f6ceaa2d232ffac70c9afaeb3dc0816337d39a7c93e39c2dee0b")