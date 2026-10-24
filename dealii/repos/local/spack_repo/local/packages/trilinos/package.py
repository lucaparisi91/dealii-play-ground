# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)
#
# Local override: with the Cray PE `gcc@14.2` external the fortran compiler
# is the driver wrapper `ftn`, which is not available in spack's build env.
# Guard the `-lgfortran` runtime probe so its absence doesn't abort ldflags
# computation (that flag is only needed for OSX/clang-with-gfortran).

import os

from spack_repo.builtin.packages.trilinos.package import Trilinos as BuiltinTrilinos

from spack.package import *


class Trilinos(BuiltinTrilinos):
    """Trilinos with a fortran-runtime probe that tolerates the missing
    Cray PE `ftn` wrapper in the build environment."""

    def flag_handler(self, name, flags):
        spec = self.spec
        is_cce = spec.satisfies("%cce")

        if name == "cxxflags":
            if "+mumps" in spec:
                flags.append("-DMUMPS_5_0")
            if "+stk platform=darwin" in spec:
                flags.append("-DSTK_NO_BOOST_STACKTRACE")
            if "+stk%intel" in spec:
                flags.append("-no-ipo")
            if "+wrapper" in spec:
                flags.append("--expt-extended-lambda")
            if spec.satisfies("%oneapi@2025:"):
                flags.append(
                    "-Wno-error=missing-template-arg-list-after-template-kw "
                    "-Wno-missing-template-arg-list-after-template-kw"
                )
        elif name == "ldflags":
            if spec.satisfies("%cce@:14"):
                flags.append("-fuse-ld=gold")
            if spec.satisfies("platform=linux ~cuda"):
                flags.append("-Wl,--as-needed")
            elif spec.satisfies("+stk +shared platform=darwin"):
                flags.append("-Wl,-undefined,dynamic_lookup")

            # Fortran lib (assumes clang is built with gfortran!)
            if spec.satisfies("+fortran %fortran=gcc"):
                try:
                    fc = Executable(self.compiler.fc)
                    libgfortran = fc(
                        "--print-file-name",
                        "libgfortran." + shared_library_suffix(spec),
                        output=str,
                    ).strip()
                    if libgfortran == "libgfortran." + shared_library_suffix(spec):
                        libgfortran = fc("--print-file-name", "libgfortran.a", output=str).strip()
                    flags.append("-L{0} -lgfortran".format(os.path.dirname(libgfortran)))
                except Exception as e:
                    # e.g. Cray PE `ftn` wrapper not resolvable in build env:
                    # the -L/-lgfortran flags are only needed on OSX with clang,
                    # so skip them rather than aborting the build.
                    tty.warn(
                        "Trilinos: fortran runtime probe skipped ({0}); "
                        "continuing without -lgfortran".format(e)
                    )

        if is_cce:
            return (None, None, flags)
        return (flags, None, None)