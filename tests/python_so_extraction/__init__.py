import requests
import os
from os.path import basename
import hashlib
import shutil
import pathlib

from conda_package_handling import api as cph_api
import pytest

from symbol_exporter import python_so_extractor

CACHE_DIR = pathlib.Path(__file__).parent / ".cache"
CACHE_DIR.mkdir(exist_ok=True)


def compare(url, checksum, filename, module_name, expected, *, xmissing=False):
    package_dir = download_sample(url, checksum)

    python_so_extractor.disassembled_cache = {}
    results = python_so_extractor.parse_file(package_dir / filename, module_name)
    actual = {x["name"] for x in results["methods"]}
    actual |= {x["name"] for x in results["objects"]}
    diff = (actual - expected)
    assert not diff, (f"Found {len(diff)} extra keys", diff)
    diff = (expected - actual)
    if xmissing:
        assert diff, "Unexpectedly passed!"
        pytest.xfail(f"{len(diff)} out of {len(expected)} were not found (known issue)")
    else:
        assert not diff, (f"Failed to find {len(diff)} out of {len(expected)} keys", diff)


def download_sample(url, checksum):
    filename = CACHE_DIR / basename(url)
    if not filename.exists():
        print(f"Downloading {url}")
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with filename.open("wb") as f:
                shutil.copyfileobj(r.raw, f)

    md5 = hashlib.md5()
    with filename.open("rb") as f:
        while data := f.read(1024**2):
            md5.update(data)
    if md5.hexdigest() != checksum:
        raise RuntimeError(f"Hash mismatch for {filename}, expected {checksum} got {md5.hexdigest()}")

    target_dir = pathlib.Path(str(filename).replace(".tar.bz2", "").replace(".conda", ""))
    if not target_dir.is_dir():
        cph_api.extract(str(filename), str(target_dir))
    
    return target_dir




# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/linux-64/gh-1.1.0-h375a9b1_0.tar.bz2#0f58b1cf244ac450711c7c65a3d9f3ac
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/linux-64/micromamba-0.7.14-he9b6cbd_0.tar.bz2#e8be734a8e0af72f323012cbcd4f971a
# https://conda.anaconda.org/conda-forge/linux-64/_libgcc_mutex-0.1-conda_forge.tar.bz2#d7c89558ba9fa0495403155b64376d81
# https://repo.anaconda.com/pkgs/main/linux-64/ca-certificates-2021.1.19-h06a4308_0.conda#c73203541f779cf79629e9dbe62f5e0b
# https://conda.anaconda.org/conda-forge/noarch/conda-forge-pinning-2020.06.24.16.31.11-0.tar.bz2#a7f7f734a7e0c9dadf1acefe36707147
# https://repo.anaconda.com/pkgs/main/linux-64/conda-standalone-4.8.3-h18fab7e_11.conda#a11f48ba0fe1c4c28f07cec7bb259f91
# https://conda.anaconda.org/conda-forge/linux-64/ld_impl_linux-64-2.34-h53a641e_4.tar.bz2#3d09e314cb01bf9935bbff32ddb7c781
# https://conda.anaconda.org/conda-forge/linux-64/libstdcxx-ng-9.3.0-hdf63c60_14.tar.bz2#e1dd88e09cea773aef5053a44d601565
# https://conda.anaconda.org/conda-forge/linux-64/libgomp-9.3.0-h24d8f2e_14.tar.bz2#f7963ba2ccc169be017d6b6926f49727
# https://conda.anaconda.org/conda-forge/linux-64/_openmp_mutex-4.5-0_gnu.tar.bz2#3053d142226093f417abe884f2ab6620
# https://conda.anaconda.org/conda-forge/linux-64/libgcc-ng-9.3.0-h24d8f2e_14.tar.bz2#68e816ab7a4b4954b475131a4819802d
# https://conda.anaconda.org/conda-forge/linux-64/bzip2-1.0.8-h516909a_2.tar.bz2#b3a914cd2f2ba2dc18121e0194143c85
# https://repo.anaconda.com/pkgs/main/linux-64/expat-2.2.9-he6710b0_2.conda#c51386e3931ddd81a5f3473c5879fff2
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/linux-64/fakechroot-2.20.1-h516909a_0.tar.bz2#28a33c0fa764c2588f6d731d7c1d47e2
# https://conda.anaconda.org/conda-forge/linux-64/icu-67.1-he1b5a44_0.tar.bz2#7ced6a5e5c94726af797d2b5a2b09228
# https://conda.anaconda.org/conda-forge/linux-64/libffi-3.2.1-he1b5a44_1007.tar.bz2#11389072d7d6036fd811c3d9460475cd
# https://conda.anaconda.org/conda-forge/linux-64/libiconv-1.16-h516909a_0.tar.bz2#5c0f338a513a2943c659ae619fca9211
# https://conda.anaconda.org/conda-forge/linux-64/liblief-0.9.0-hf8a498c_1.tar.bz2#cbafc2f95bc4650ec5128c9b42a38be0
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/linux-64/libunwind-1.2.1-hf484d3e_1000.tar.bz2#f061dd573566bf45b5880c4cfec29204
# https://conda.anaconda.org/conda-forge/linux-64/lz4-c-1.9.3-h9c3ff4c_0.tar.bz2#4eb64ee0d5cd43096ffcf843c76b05d4
# https://conda.anaconda.org/conda-forge/linux-64/lzo-2.10-h14c3975_1000.tar.bz2#fdfe358359c80bc633f632f4b2754d32
# https://conda.anaconda.org/conda-forge/linux-64/ncurses-6.2-he1b5a44_1.tar.bz2#d3da4932f3d8e6b3c81fcf177d1e6eab
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/linux-64/openssl-1.1.1j-h7f98852_0.tar.bz2#f91545bee2ac8cf86f1dc53e55a7bb2b
# https://conda.anaconda.org/conda-forge/linux-64/patchelf-0.10-he1b5a44_0.tar.bz2#fb85a0f671dca5993def7fcf0645788d
# https://repo.anaconda.com/pkgs/main/linux-64/pcre-8.44-he6710b0_0.conda#e337926bb92177a2a3aded95a895470d
# https://conda.anaconda.org/conda-forge/linux-64/perl-5.26.2-h516909a_1006.tar.bz2#7159f7a31fb4176bac015a35ca8f199f
# file:///home/cburr/miniconda3/conda-bld/linux-64/prmon-2.0.2-h6bb024c_0.tar.bz2#eae2dfd120a454deac19ac5e5bc78ddb
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/linux-64/reproc-14.2.1-h36c2ea0_0.tar.bz2#72dc07a3b9641f9f530bf72e2c7a12b2
# https://conda.anaconda.org/conda-forge/linux-64/ripgrep-12.1.0-h516909a_0.tar.bz2#6b79fb7442542cc11d300e10c5f6642e
# https://conda.anaconda.org/conda-forge/linux-64/xz-5.2.5-h516909a_0.tar.bz2#f614b8373daba12b7c8da72c35669a9a
# https://conda.anaconda.org/conda-forge/linux-64/yaml-0.2.4-h516909a_0.tar.bz2#ba81b3f1827d44250b0fdb17c35c2236
# https://conda.anaconda.org/conda-forge/linux-64/zlib-1.2.11-h516909a_1006.tar.bz2#eb59ca0a6123517e35bae003be4b4bfe
# https://conda.anaconda.org/conda-forge/linux-64/gettext-0.19.8.1-hc5be6a0_1002.tar.bz2#8c2f1de42f9eec059418f3083f03cabc
# https://repo.anaconda.com/pkgs/main/linux-64/libedit-3.1.20181209-hc058e9b_0.conda#594c05f769516b55c004eada4fc9ea74
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/linux-64/libsolv-0.7.17-h780b84a_0.tar.bz2#1c1e60fddcd687302a40b2f5e4c13d53
# https://conda.anaconda.org/conda-forge/linux-64/libssh2-1.9.0-hab1572f_2.tar.bz2#42451c9ceeb807f53e9277657909307f
# https://conda.anaconda.org/conda-forge/linux-64/libxml2-2.9.10-h68273f3_2.tar.bz2#0315cae0468a1e17f1e7fad5b13d53f8
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/linux-64/ncdu-1.15-he28a2e2_1.tar.bz2#cf063886c649b9482a49b35a9d4c234f
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/linux-64/py-spy-0.3.3-h3633216_1.tar.bz2#4465dce3b8386b91694fb741a90b24b0
# https://conda.anaconda.org/conda-forge/linux-64/readline-8.0-he28a2e2_2.tar.bz2#4d0ae8d473f863696088f76800ef9d38
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/linux-64/reproc-cpp-14.2.1-h58526e2_0.tar.bz2#d1d5d63dafc7b2e484d02823606db5d9
# https://conda.anaconda.org/conda-forge/linux-64/tk-8.6.10-hed695b0_0.tar.bz2#9a3e126468fa7fb6a54caad41b5a2d45
# https://conda.anaconda.org/conda-forge/linux-64/zstd-1.4.8-ha95c52a_1.tar.bz2#ed4dbbaf7d81423678632bf982f45ede
# https://conda.anaconda.org/conda-forge/linux-64/bash-5.0.018-h0a1914f_0.tar.bz2#9155f66516bf60afe5e88d68345401be
# https://conda.anaconda.org/conda-forge/linux-64/krb5-1.17.1-h2fd8d38_0.tar.bz2#f03ea3ccb1bd144d0db282ca6ee1cd97
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/linux-64/libarchive-3.5.1-h3f442fb_1.tar.bz2#1579ccb4f14593e95627bcdb29af953a
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/linux-64/socat-1.7.3.4-hbf9578c_1.tar.bz2#9a46cf070fe64d7e28d04a746843bd2e
# https://repo.anaconda.com/pkgs/main/linux-64/sqlite-3.31.1-h7b6447c_0.conda#c2cae59a837775a03aed11469994981c
# https://conda.anaconda.org/conda-forge/linux-64/libcurl-7.71.1-hcdd3856_2.tar.bz2#ad422fe2a407324fe93c832ff2d4740d
# https://conda.anaconda.org/conda-forge/linux-64/openshift-cli-4.1.0-hfdc87ad_1.tar.bz2#32543af0f19b7ce9aa7217b2f4796aad
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/linux-64/python-3.7.6-cpython_he5300dc_6.tar.bz2#9c5305f3a5f24f74fb87eb6d67e4053c
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/noarch/alabaster-0.7.12-py_0.tar.bz2#2489a97287f90176ecdc3ca982b4b0a0
# https://conda.anaconda.org/conda-forge/noarch/appdirs-1.4.3-py_1.tar.bz2#79ea201c0ff86b098d3e3e3fa45505cd
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/noarch/archspec-0.1.1-pyh9f0ad1d_0.tar.bz2#7b225148929d3cb0cbda7f769f2cb7d1
# https://conda.anaconda.org/conda-forge/noarch/attrs-19.3.0-py_0.tar.bz2#5ddf9ee0eb95aac1d3881a8e3df5a1fa
# https://conda.anaconda.org/conda-forge/noarch/backcall-0.1.0-py_0.tar.bz2#a6d55d275ba454de578438ae587d7d86
# https://repo.anaconda.com/pkgs/main/linux-64/blinker-1.4-py37_0.conda#2efb99772b8bcd253398eaede90fe3b1
# https://conda.anaconda.org/conda-forge/noarch/boolean.py-3.7-py_0.tar.bz2#57004d9b649561b935d23b66af8e138c
# https://conda.anaconda.org/conda-forge/noarch/click-7.1.2-pyh9f0ad1d_0.tar.bz2#bd50a970ce07e660c319fdc4d730d3f1
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/noarch/colorama-0.4.3-py_0.tar.bz2#9cf68a6826504feedbfd646bc4d1ca14
# https://conda.anaconda.org/conda-forge/linux-64/curl-7.71.1-he644dc0_2.tar.bz2#70bfcde967f25a177beac61a9b8b65e6
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/linux-64/dataclasses-0.7-py37_0.tar.bz2#a83c38ed7ea1288bc530d95474be71a6
# https://conda.anaconda.org/conda-forge/noarch/decorator-4.4.2-py_0.tar.bz2#d2eabb9cabd212e1ec6a9463bd846243
# https://conda.anaconda.org/conda-forge/noarch/distlib-0.3.1-pyh9f0ad1d_0.tar.bz2#db990401a267e2b15854af5f3f84f763
# https://conda.anaconda.org/conda-forge/noarch/filelock-3.0.12-pyh9f0ad1d_0.tar.bz2#7544ed05bbbe9bb687bc9bcbe4d6cb46
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/linux-64/glib-2.65.0-h6f030ca_0.tar.bz2#b0de00a186a544e2bdaed9765d97868f
# https://conda.anaconda.org/conda-forge/noarch/glob2-0.7-py_0.tar.bz2#1f3a88e65e61216e1d475135922dbf6a
# https://conda.anaconda.org/conda-forge/noarch/idna-2.9-py_1.tar.bz2#846ba802162eb14046e303053b42ad61
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/noarch/imagesize-1.2.0-py_0.tar.bz2#5879bd2c4b399a5072468e5fe587bf1b
# https://conda.anaconda.org/conda-forge/noarch/ipython_genutils-0.2.0-py_1.tar.bz2#5071c982548b3a20caf70462f04f5287
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/noarch/jeepney-0.4.3-py_0.tar.bz2#0a9435149140c0e50bf18d79bd07c0ac
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/noarch/json5-0.9.5-pyh9f0ad1d_0.tar.bz2#10759827a94e6b14996e81fb002c0bda
# https://conda.anaconda.org/conda-forge/noarch/mccabe-0.6.1-py_1.tar.bz2#a326cb400c1ccd91789f3e7d02124d61
# https://conda.anaconda.org/conda-forge/noarch/parso-0.7.0-pyh9f0ad1d_0.tar.bz2#12163ee7025dcbad5de7ad23ff31722c
# https://conda.anaconda.org/conda-forge/noarch/pathspec-0.8.0-pyh9f0ad1d_0.tar.bz2#8eeecbb67554f588ba70bea7018bc1c0
# https://conda.anaconda.org/conda-forge/noarch/pkginfo-1.5.0.1-py_0.tar.bz2#4bdd776f2eb65244c27c5f61638a507c
# https://conda.anaconda.org/conda-forge/noarch/ptyprocess-0.6.0-py_1001.tar.bz2#0c3a56f1ab48cfb002c69b48f9e1ddc6
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/noarch/py-1.9.0-pyh9f0ad1d_0.tar.bz2#82beb69c4e05d65702bbde3c63d6ef58
# https://conda.anaconda.org/conda-forge/noarch/pycparser-2.20-py_0.tar.bz2#e0a3e66aaaac33386b3cf35b5523b2ce
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/linux-64/pyelftools-0.26-py37_0.tar.bz2#f51c531b43190ec0ceda0280b4a98dd4
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/noarch/pyparsing-2.4.7-pyh9f0ad1d_0.tar.bz2#626c4f20d5bf06dcec9cf2eaa31725c7
# https://conda.anaconda.org/conda-forge/linux-64/python-libarchive-c-2.9-py37_0.tar.bz2#fd32ac66a19379dd3fc5ad71902c12f2
# https://conda.anaconda.org/conda-forge/linux-64/python_abi-3.7-1_cp37m.tar.bz2#658a5c3d766bfc6574480204b10a6f20
# https://conda.anaconda.org/conda-forge/noarch/pytz-2020.1-pyh9f0ad1d_0.tar.bz2#e52abc1f0fd70e05001c1ceb2696f625
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/noarch/rfc3986-1.4.0-pyh9f0ad1d_0.tar.bz2#4dd11e722e5a29afc55e5d7f15782130
# https://conda.anaconda.org/conda-forge/noarch/six-1.15.0-pyh9f0ad1d_0.tar.bz2#1eec421f0f1f39e579e44e4a5ce646a2
# https://conda.anaconda.org/conda-forge/noarch/smmap-3.0.4-pyh9f0ad1d_0.tar.bz2#102f29e2015d9311c86996a20ce866ae
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/noarch/snowballstemmer-2.0.0-py_0.tar.bz2#fa34c3e7fb741022eb79169c354ca1ae
# https://conda.anaconda.org/conda-forge/noarch/sphinxcontrib-applehelp-1.0.2-py_0.tar.bz2#20b2eaeaeea4ef9a9a0d99770620fd09
# https://conda.anaconda.org/conda-forge/noarch/sphinxcontrib-devhelp-1.0.2-py_0.tar.bz2#68e01cac9d38d0e717cd5c87bc3d2cc9
# https://conda.anaconda.org/conda-forge/noarch/sphinxcontrib-htmlhelp-1.0.3-py_0.tar.bz2#4508a40465ebf0105e52f7194f299411
# https://conda.anaconda.org/conda-forge/noarch/sphinxcontrib-jsmath-1.0.1-py_0.tar.bz2#67cd9d9c0382d37479b4d306c369a2d4
# https://conda.anaconda.org/conda-forge/noarch/sphinxcontrib-qthelp-1.0.3-py_0.tar.bz2#d01180388e6d1838c3e1ad029590aa7a
# https://conda.anaconda.org/conda-forge/noarch/sphinxcontrib-serializinghtml-1.1.4-py_0.tar.bz2#8ea6a8036e28dba8827d35c764709358
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/noarch/tabulate-0.8.7-pyh9f0ad1d_0.tar.bz2#229780178ffe9121c873e00ba8de39bf
# https://conda.anaconda.org/conda-forge/noarch/toml-0.10.1-pyh9f0ad1d_0.tar.bz2#ca47d0ef822fd23b7ec9771a36645e5e
# https://conda.anaconda.org/conda-forge/noarch/toolz-0.10.0-py_0.tar.bz2#9b38c091d24a308daf386f1e82d9d3a9
# https://repo.anaconda.com/pkgs/main/noarch/tqdm-4.44.1-py_0.conda#5a680a380e9ca63fa6eb039f7b31ffb6
# https://conda.anaconda.org/conda-forge/linux-64/typed-ast-1.4.1-py37h516909a_0.tar.bz2#8ce1dc4eaf70204b3a3544f52a5939f8
# https://conda.anaconda.org/conda-forge/noarch/typing_extensions-3.7.4.2-py_0.tar.bz2#235133b5ac204ecadf84cd07bab4fbe3
# https://conda.anaconda.org/conda-forge/noarch/wcwidth-0.1.9-pyh9f0ad1d_0.tar.bz2#ef10a99c7570762fa2a69218c171dbc8
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/noarch/webencodings-0.5.1-py_1.tar.bz2#3563be4c5611a44210d9ba0c16113136
# https://conda.anaconda.org/conda-forge/noarch/zipp-3.1.0-py_0.tar.bz2#61948e426a3a3ec1fa7c90a44c2585d1
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/noarch/babel-2.8.0-py_0.tar.bz2#2d6d06e3b9884b2446ed7d6e10db9eb3
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/linux-64/certifi-2020.12.5-py37h89c1867_1.tar.bz2#fb121f213009359498ada17a9e6d775f
# https://conda.anaconda.org/conda-forge/linux-64/cffi-1.14.0-py37hd463f26_0.tar.bz2#e8f964de28087a1a68f5be2c4449f3b0
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/noarch/cfgv-3.2.0-py_0.tar.bz2#4972efcb3e2cbd3954b24a17266be25c
# https://conda.anaconda.org/conda-forge/linux-64/chardet-3.0.4-py37hc8dfbb8_1006.tar.bz2#9ac087b0b93ba7448ed20de438c23bc6
# https://conda.anaconda.org/conda-forge/linux-64/conda-package-handling-1.6.0-py37h8f50634_2.tar.bz2#c9e8d8dffd135b913beb4d333d603ae4
# https://repo.anaconda.com/pkgs/main/linux-64/dbus-1.13.16-hb2f20db_0.conda#8abe4daf6a5d089ea4babe628d0e97dd
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/linux-64/docutils-0.16-py37hc8dfbb8_1.tar.bz2#df1a07f09d713454fb016823aad4e9be
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/linux-64/editdistance-0.5.3-py37hcd2ae1e_3.tar.bz2#e9c9fe028748305864f776ebdf7a823b
# https://conda.anaconda.org/conda-forge/linux-64/future-0.18.2-py37hc8dfbb8_1.tar.bz2#035a07820788119b9903bf568f0d5b7e
# https://conda.anaconda.org/conda-forge/linux-64/git-2.28.0-pl526h5e3e691_1.tar.bz2#feaf4e1b10e5a76b62e09d66ae98fa07
# https://conda.anaconda.org/conda-forge/noarch/gitdb-4.0.5-py_0.tar.bz2#94c135f9db6e89c6a848d3f7ae2cc66b
# https://conda.anaconda.org/conda-forge/linux-64/importlib-metadata-1.6.0-py37hc8dfbb8_0.tar.bz2#351c1b17a460cc6032054b89870e2e36
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/linux-64/inotify_simple-1.3.5-py37hc8dfbb8_1.tar.bz2#3355d5aa39c015e6993c3ab25649b05d
# https://repo.anaconda.com/pkgs/main/linux-64/isodate-0.6.0-py37_0.conda#12a1470b27d007890b70947f0d95c7b2
# https://conda.anaconda.org/conda-forge/linux-64/jedi-0.17.0-py37hc8dfbb8_0.tar.bz2#bacd78e8a58fa57fcacc3a8df1177343
# https://conda.anaconda.org/conda-forge/linux-64/lazy-object-proxy-1.4.3-py37h8f50634_2.tar.bz2#ca5a654950e8cd78e7e749d0eeae56f1
# https://conda.anaconda.org/conda-forge/noarch/license-expression-1.2-py_0.tar.bz2#72564c688f3ac55eddc7b93e4ab8bd4f
# https://conda.anaconda.org/conda-forge/linux-64/markupsafe-1.1.1-py37h8f50634_1.tar.bz2#3a1f9e93d5bed65a9875eb2e5805cf0d
# https://conda.anaconda.org/conda-forge/linux-64/mypy_extensions-0.4.3-py37hc8dfbb8_1.tar.bz2#3770dbc2429c6fb508ce72034a898cfd
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/noarch/packaging-20.4-pyh9f0ad1d_0.tar.bz2#6d160f7346ac815500b5475d9a0f88a9
# https://conda.anaconda.org/conda-forge/linux-64/pexpect-4.8.0-py37hc8dfbb8_1.tar.bz2#fda2ad946f9f5b7ce3531cc34ab262e9
# https://conda.anaconda.org/conda-forge/linux-64/pickleshare-0.7.5-py37hc8dfbb8_1001.tar.bz2#da9fda4a608e5de6990bf16f79c4ae1c
# https://conda.anaconda.org/conda-forge/linux-64/psutil-5.7.0-py37h8f50634_1.tar.bz2#9c5b3e84c0952a7cacb069c18ae1932a
# https://conda.anaconda.org/conda-forge/linux-64/pycosat-0.6.3-py37h8f50634_1004.tar.bz2#64e05681e3e672b8190688f7fe56ef46
# https://conda.anaconda.org/conda-forge/linux-64/pycrypto-2.6.1-py37h8f50634_1004.tar.bz2#972c15bab1559d0dec151d1486d80f0d
# https://conda.anaconda.org/conda-forge/linux-64/pyrsistent-0.16.0-py37h8f50634_0.tar.bz2#0d30d9cd284a3b9797291e29ae9d8129
# https://conda.anaconda.org/conda-forge/linux-64/pysocks-1.7.1-py37hc8dfbb8_1.tar.bz2#3e3574f5f72cfb377ea86c87ca4a4599
# https://conda.anaconda.org/conda-forge/noarch/python-dateutil-2.8.1-py_0.tar.bz2#0d0150ed9c2d25817f5324108d3f7571
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/noarch/python-utils-2.4.0-py_0.tar.bz2#ecbb1d56686f4d2064b8851f7ef9a6e6
# https://conda.anaconda.org/conda-forge/linux-64/pyyaml-5.3.1-py37h8f50634_0.tar.bz2#13495f8abe3fa4e8905439257d1132d4
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/linux-64/rapidfuzz-0.11.0-py37h3340039_0.tar.bz2#2fdbb5185f34665a3cbf93f543cc6846
# https://conda.anaconda.org/conda-forge/linux-64/regex-2020.5.14-py37h8f50634_0.tar.bz2#f1ed5af8034e3e9f9593c8bfe5e4fd53
# https://conda.anaconda.org/conda-forge/linux-64/ruamel.yaml.clib-0.2.0-py37h8f50634_1.tar.bz2#71717a66629f873f5283b5cdb0f995dc
# https://conda.anaconda.org/conda-forge/linux-64/ruamel_yaml-0.15.80-py37h8f50634_1001.tar.bz2#a7314a2fe6a28b4d6c8029c1e563f653
# https://conda.anaconda.org/conda-forge/linux-64/soupsieve-2.0.1-py37hc8dfbb8_0.tar.bz2#2a7081d9ecc5ccd34af6739bb74512cc
# https://conda.anaconda.org/conda-forge/linux-64/traitlets-4.3.3-py37hc8dfbb8_1.tar.bz2#d565e0456c21e6aa521f79889a5da1ab
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/noarch/typing-extensions-3.7.4.2-0.tar.bz2#1ea334fb96682066db6ff47907f1aae4
# https://conda.anaconda.org/conda-forge/linux-64/wrapt-1.12.1-py37h8f50634_1.tar.bz2#d6f832e746eb1ebd18188296f0e3bb6f
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/linux-64/youtube-dl-2020.11.1.1-py37h89c1867_0.tar.bz2#725fa1bd9322143b5cd8d15742484f7f
# https://conda.anaconda.org/conda-forge/linux-64/beautifulsoup4-4.9.1-py37hc8dfbb8_0.tar.bz2#aa68567528981eb71d172b50e88b2f8f
# https://conda.anaconda.org/conda-forge/noarch/black-20.8b1-py_1.tar.bz2#e555d6b71ec916c3dc4e6e3793cc9796
# https://conda.anaconda.org/conda-forge/linux-64/brotlipy-0.7.0-py37h8f50634_1000.tar.bz2#32f5c3392501d6f5f20a24be76e03702
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/linux-64/cmarkgfm-0.4.2-py37h516909a_2.tar.bz2#eabbfa9a77fe70e47cd71ea86e5736a4
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/noarch/commonmark-0.9.1-py_0.tar.bz2#6aa0173c14befcd577ded130cf6f22f5
# https://conda.anaconda.org/conda-forge/linux-64/cryptography-2.9.2-py37hb09aad4_0.tar.bz2#135d39a06efedcdedd4af65026f5a634
# https://conda.anaconda.org/conda-forge/noarch/deprecated-1.2.10-pyh9f0ad1d_0.tar.bz2#f8a0f3425a523903e86296072e267e13
# https://conda.anaconda.org/conda-forge/noarch/gitpython-3.1.7-py_0.tar.bz2#6aa54e476c96b36535603b67754e4f91
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/noarch/identify-1.5.13-pyh44b312d_0.tar.bz2#21cf1d0cd31bacebc9fc52b50f0c833b
# https://conda.anaconda.org/conda-forge/noarch/importlib_metadata-1.6.0-0.tar.bz2#5ab13b586ea79f4324a1d4d5de1f04fb
# https://conda.anaconda.org/conda-forge/linux-64/jupyter_core-4.6.3-py37hc8dfbb8_1.tar.bz2#2169191b3df60024143e88aa047454ae
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/noarch/progressbar2-3.53.1-pyh9f0ad1d_0.tar.bz2#a1600b4f320eb5ad2edc1d6eadc62211
# https://conda.anaconda.org/conda-forge/linux-64/scrypt-0.8.15-py37hb09aad4_0.tar.bz2#7afa5bf698f27a721f08fb42accce2fc
# https://conda.anaconda.org/conda-forge/linux-64/setuptools-47.1.0-py37hc8dfbb8_0.tar.bz2#c6d173073579045d944c6ef7214ae53c
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/linux-64/virtualenv-20.0.35-py37hc8dfbb8_0.tar.bz2#32379279fa8978b968f3def520893cd9
# https://repo.anaconda.com/pkgs/main/linux-64/astroid-2.3.3-py37_0.conda#40ac7bd23d2ca5f934ffe294ad4faceb
# https://conda.anaconda.org/conda-forge/noarch/bleach-3.2.1-pyh9f0ad1d_0.tar.bz2#d4506316b85679972c0b78d4d1c0b701
# https://conda.anaconda.org/conda-forge/noarch/clyent-1.2.2-py_1.tar.bz2#b9ee3fdf59f49883497741509ea364b6
# https://conda.anaconda.org/conda-forge/linux-64/isort-4.3.21-py37hc8dfbb8_1.tar.bz2#e1042bf254530d1a3cc97dd7cec7c3b7
# https://conda.anaconda.org/conda-forge/noarch/jinja2-2.11.2-pyh9f0ad1d_0.tar.bz2#e8a5d614d1a27bdba00059ca062a0551
# https://repo.anaconda.com/pkgs/main/noarch/joblib-0.14.1-py_0.conda#f5e4e8dc665be74064c050ccec9a069d
# https://conda.anaconda.org/conda-forge/linux-64/jsonschema-3.2.0-py37hc8dfbb8_1.tar.bz2#3bbfbc1c12652fc35a225180d7aeff19
# https://conda.anaconda.org/conda-forge/noarch/networkx-2.5-py_0.tar.bz2#d836ad8453c22192357707026ca21653
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/noarch/nodeenv-1.5.0-pyh9f0ad1d_0.tar.bz2#59e109cb68807a14b71f3f973b93747b
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/linux-64/pluggy-0.13.1-py37hc8dfbb8_3.tar.bz2#1454d9425b13fe975f37da68fda1f674
# https://conda.anaconda.org/conda-forge/noarch/pygments-2.6.1-py_0.tar.bz2#37736a64e169c430eac98a46ddc1ac4a
# https://repo.anaconda.com/pkgs/main/linux-64/pyjwt-1.7.1-py37_0.conda#798fae27b68fe4b237c9b40fda7f3496
# https://conda.anaconda.org/conda-forge/noarch/pyopenssl-19.1.0-py_1.tar.bz2#ef3d970a6de9bc902d233e59f746b7cd
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/linux-64/ruamel.yaml-0.16.12-py37h5e8e339_2.tar.bz2#93d2ddcc1fd02bd503c2206027576b5e
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/linux-64/secretstorage-3.1.2-py37hc8dfbb8_1.tar.bz2#b9e925a2e071539755afd86692860561
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/noarch/setuptools-scm-5.0.1-pyhd3deb0d_0.tar.bz2#4a2aca8eb8f90c907a54154347acff61
# https://conda.anaconda.org/conda-forge/noarch/wheel-0.34.2-py_1.tar.bz2#1a3f64dbee07e02a8f1de36b5b5e98ee
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/linux-64/keyring-21.4.0-py37hc8dfbb8_1.tar.bz2#9ed07fdba8c46142cd9e5a863799a519
# https://conda.anaconda.org/conda-forge/noarch/nbformat-5.0.6-py_0.tar.bz2#5583740b20b8d4d72e9d45b5838de751
# https://repo.anaconda.com/pkgs/main/noarch/oauthlib-3.1.0-py_0.conda#c17d4f150993bb3181a2bb4d0b3fdeef
# https://conda.anaconda.org/conda-forge/noarch/pip-20.1.1-py_1.tar.bz2#5e42afe5672d5baf3d9d2260239aa923
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/linux-64/pre-commit-2.10.0-py37h89c1867_0.tar.bz2#3e41fc4547c3140ccbc8d9c03ec56ea3
# https://conda.anaconda.org/conda-forge/noarch/prompt-toolkit-3.0.5-py_0.tar.bz2#a280c0f4675f808df0cd79c8c5eaaa07
# https://repo.anaconda.com/pkgs/main/linux-64/pylint-2.4.4-py37_0.conda#1c632e12b239a69f073606d69961fb6b
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/noarch/readme_renderer-24.0-pyh9f0ad1d_0.tar.bz2#8b8301b19bafd23c69375befa10c2149
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/linux-64/rich-9.1.0-py37hc8dfbb8_0.tar.bz2#51182713b4c26d00d354bf61d2afca5d
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/noarch/ruamel.yaml.jinja2-0.2.4-py_1.tar.bz2#12f4cc11476f0f9ef90102792732ee38
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/noarch/setuptools_scm-5.0.1-hd8ed1ab_0.tar.bz2#a646405c41a50cf223e1e04a49e3b2b9
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/linux-64/tox-3.20.1-py37hc8dfbb8_1.tar.bz2#e2900feb92efdfee7efea0de3e68096e
# https://conda.anaconda.org/conda-forge/noarch/urllib3-1.25.9-py_0.tar.bz2#8cb5f508d95109c9395141ca6ceb6ec5
# https://conda.anaconda.org/conda-forge/noarch/prompt_toolkit-3.0.5-0.tar.bz2#1fba0827c92e97d6bc0a40397a8fbd81
# https://conda.anaconda.org/conda-forge/noarch/requests-2.23.0-pyh8c360ce_2.tar.bz2#73055fb278196cccbf3c90e6d7115533
# https://repo.anaconda.com/pkgs/main/linux-64/anaconda-client-1.7.2-py37_0.conda#5e8085c658b7cfc53411a7b298ad5aac
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/linux-64/conda-4.9.2-py37h89c1867_0.tar.bz2#8c24efe074ff6c56eec13ab5e0829302
# https://repo.anaconda.com/pkgs/main/linux-64/ipython-7.13.0-py37h5ca1d4c_0.conda#6b8d4cfa9699d4b5d663d4985bd79dd1
# https://conda.anaconda.org/conda-forge/noarch/pygithub-1.51-py_0.tar.bz2#1c07a7ae93bb69540001e903958b34f9
# https://repo.anaconda.com/pkgs/main/noarch/requests-oauthlib-1.3.0-py_0.conda#a889394d246d3d475ced7df1314abdaa
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/noarch/requests-toolbelt-0.9.1-py_0.tar.bz2#402668adee8fcba9a9c265cdc2a88f5a
# https://conda.anaconda.org/conda-forge/noarch/sphinx-3.2.1-py_0.tar.bz2#6775ce3cbf77a9447eacd1592858a738
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/linux-64/conda-build-3.21.4-py37h89c1867_0.tar.bz2#d3f12f8b4c8bb9186e06755cfe2f0335
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/noarch/conda-tree-0.1.0-py_0.tar.bz2#1b52473de712e6d3ae76d67bfff3d201
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/linux-64/constructor-3.2.0-py37h89c1867_1.tar.bz2#ff86468d2d2d76d1b6e7648488e4c3e6
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/noarch/ipdb-0.13.4-pyhd3deb0d_0.tar.bz2#b6e9e536a43b76c5341fe061177d65c4
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/linux-64/mamba-0.7.14-py37h7f483ca_0.tar.bz2#489d89d4fd43dca9cc491963e4586478
# https://conda.anaconda.org/conda-forge/noarch/msrest-0.6.17-pyh9f0ad1d_0.tar.bz2#9c8a78cb565b438372953109ca94add4
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/linux-64/stdlib-list-0.6.0-py37_0.tar.bz2#f3c398eb30e9f5d45ab7764f09801d36
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/linux-64/twine-3.2.0-py37hc8dfbb8_0.tar.bz2#4586a9aacd0c490b32f8ddef6dbeadee
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/linux-64/boa-0.3.5-py37h89c1867_0.tar.bz2#68e2a4691072e83e3f12b83dbc46c433
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/noarch/grayskull-0.8.5-pyhd8ed1ab_0.tar.bz2#6003b8d4501caf16acc8411930b2f5d6
# https://conda.anaconda.org/conda-forge/noarch/vsts-python-api-0.1.22-py_0.tar.bz2#35edd007bb1e43a620fbb775f75effc6
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/noarch/conda-smithy-3.8.6-pyhd8ed1ab_0.tar.bz2#9e8e6c99130f242fab21428312e439ca
# https://conda.anaconda.org/t/ch-6ffeaf66-e1eb-4153-864f-2fecc5a53091/conda-forge/noarch/greyskull-0.8.5-hd8ed1ab_0.tar.bz2#c54052977c661a63e817b3f1300989c7
