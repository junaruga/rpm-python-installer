"""
Tests for install.py

"""
import os
import re
import tempfile
from unittest import mock

import pytest

from install import Application, Cmd, InstallError, InstallSkipError, Log


@pytest.fixture
def app():
    return Application()


def test_cmd_sh_e_is_ok():
    stdout = Cmd.sh_e('pwd')
    assert not stdout


def test_cmd_sh_e_out_is_ok():
    stdout = Cmd.sh_e_out('pwd')
    assert stdout


def test_cmd_cd_is_ok():
    with pytest.helpers.reset_dir():
        tmp_dir = tempfile.gettempdir()
        Cmd.cd(tmp_dir)
        cwd = os.getcwd()
        assert cwd == tmp_dir


def test_app_init(app):
    assert app
    assert app.verbose is False
    assert app.python_path
    assert 'bin/python' in app.python_path
    assert app.rpm_path
    assert 'rpm' in app.rpm_path
    assert app.rpm_version
    assert re.match('^[\d.]+$', app.rpm_version)
    assert app.setup_py_opts == '-q'
    assert app.curl_opts == '--silent'
    assert app.is_work_dir_removed is False


def test_verify_system_status_is_ok(app):
    app.verify_system_status()
    assert True


def test_verify_system_status_is_skipped_sys_python_and_rpm_py_installed(app):
    app.is_system_python = mock.MagicMock(return_value=True)
    app.is_python_binding_installed = mock.MagicMock(return_value=True)

    with pytest.raises(InstallSkipError):
        app.verify_system_status()

    assert True


def test_verify_system_status_is_error_on_sys_py_and_rpm_py_not_installed(app):
    app.is_system_python = mock.MagicMock(return_value=True)
    app.is_python_binding_installed = mock.MagicMock(return_value=False)
    with pytest.raises(InstallError) as ei:
        app.verify_system_status()
    assert re.match('^RPM Python binding on system Python.*manually.$',
                    str(ei.value))


def test_verify_system_status_is_error_on_sys_rpm_and_missing_packages(app):
    app.is_system_rpm = mock.MagicMock(return_value=True)
    app.is_rpm_package_installed = mock.MagicMock(return_value=False)
    with pytest.raises(InstallError) as ei:
        app.verify_system_status()
    expected_message = (
        'Required RPM not installed: [rpm-libs, rpm-devel].\n'
        'Install it by "dnf install rpm-libs rpm-devel".\n'
    )
    assert expected_message == str(ei.value)


@mock.patch.object(Log, 'verbose', new=True)
def test_run(app):
    app.is_work_dir_removed = True
    app.run()
    assert True
