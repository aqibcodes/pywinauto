import os
import sys
import subprocess
import time
import unittest
import re
import mock

if sys.platform != 'win32':
    sys.path.append(".")
    from pywinauto.linux.atspi_objects import AtspiAccessible
    from pywinauto.linux.atspi_objects import AtspiDocument
    from pywinauto.linux.atspi_element_info import AtspiElementInfo
    from pywinauto.linux.atspi_element_info import known_control_types
    from pywinauto.linux.application import Application

app_name = r"gtk_example.py"


def _test_app():
    test_folder = os.path.join(os.path.dirname
                               (os.path.dirname
                                (os.path.dirname
                                 (os.path.abspath(__file__)))),
                               r"apps/Gtk_samples")
    sys.path.append(test_folder)
    return os.path.join(test_folder, app_name)


if sys.platform != 'win32':
    class AtspiElementInfoTests(unittest.TestCase):

        """Unit tests for the AtspiElementInfo class"""

        def get_app(self, name):
            for children in self.desktop_info.children():
                if children.name == name:
                    return children
            else:
                raise Exception("Application not found")

        def setUp(self):
            self.desktop_info = AtspiElementInfo()
            self.app = Application()
            self.app.start("python3 " + _test_app())
            time.sleep(1)
            self.app_info = self.get_app(app_name)

        def tearDown(self):
            self.app.kill()

        def test_can_get_desktop(self):
            self.assertEqual(self.desktop_info.class_name, "desktop frame")

        def test_can_get_childrens(self):
            apps = [children.name for children in self.desktop_info.children()]
            self.assertTrue(app_name in apps)

        def test_can_get_name(self):
            self.assertEqual(self.desktop_info.name, "main")

        def test_can_get_parent(self):
            parent = self.app_info.parent
            self.assertEqual(parent.class_name, "desktop frame")

        def test_can_get_process_id(self):
            self.assertEqual(self.app_info.process_id, self.app.process)

        def test_can_get_class_name(self):
            self.assertEqual(self.app_info.class_name, "application")

        def test_can_get_control_type_property(self):
            self.assertEqual(self.app_info.control_type, "Application")

        def test_can_get_control_type_of_all_app_descendants(self):
            for children in self.app_info.descendants():
                self.assertTrue(children.control_type in known_control_types)

        def test_control_type_equal_class_name(self):
            for children in self.app_info.descendants():
                self.assertEqual(children.control_type.lower().replace("_", " "), children.class_name)

        def test_can_get_description(self):
            # TODO find a way to add meaningful description to example application
            self.assertEqual(self.app_info.description(), "")

        def test_can_get_framework_id(self):
            dpkg_output = subprocess.check_output(["dpkg", "-s", "libgtk-3-0"]).decode(encoding='UTF-8')
            version_line = None
            for line in dpkg_output.split("\n"):
                if line.startswith("Version"):
                    version_line = line
                    break
            print(version_line)
            if version_line is None:
                raise Exception("Cant get system gtk version")
            version_pattern = "Version:\\s+(\\d+\\.\\d+\\.\\d+).*"
            r_version = re.compile(version_pattern, flags=re.MULTILINE)
            res = r_version.match(version_line)
            gtk_version = res.group(1)
            self.assertEqual(self.app_info.framework_id(), gtk_version)

        def test_can_get_framework_name(self):
            self.assertEqual(self.app_info.framework_name(), "gtk")

        def test_can_get_atspi_version(self):
            # TODO Get atspi version from loaded so
            version = self.app_info.atspi_version()
            self.assertTrue(version in ["2.0", "2.1"], msg="Unexpected AT-SPI version: {}".format(version))

        def test_can_get_rectangle(self):
            app_info = self.get_app(app_name)
            frame = app_info.children()[0]
            filler = frame.children()[0]
            rectangle = filler.rectangle
            self.assertEqual(rectangle.width(), 600)
            self.assertEqual(rectangle.height(), 200)

        def test_can_compare_applications(self):
            app_info = self.get_app(app_name)
            app_info1 = self.get_app(app_name)
            assert app_info == app_info1

        def test_can_compare_desktop(self):
            desktop = AtspiElementInfo()
            desktop1 = AtspiElementInfo()
            assert desktop == desktop1

        def test_can_get_layer(self):
            self.assertEqual(self.desktop_info.get_layer(), 3)

        def test_can_get_state_set(self):
            app_info = self.app_info.children()[0]
            app_info1 = self.app_info.children()[0].children()[0]
            print(app_info.get_state_set().get_states())
            print(app_info1.get_state_set().get_states())

    class AtspiElementInfoDocumentMockedTests(unittest.TestCase):

        """Mocked unit tests for the AtspiElementInfo.document related functionality"""

        def setUp(self):
            self.info = AtspiElementInfo()
            self.patch_get_role = mock.patch.object(AtspiAccessible, 'get_role')
            self.mock_get_role = self.patch_get_role.start()
            self.mock_get_role.return_value = known_control_types.index("Document_frame")

        def tearDown(self):
            self.patch_get_role.stop()

        def test_document_success(self):
            self.assertEqual(type(self.info.document), AtspiDocument)

        def test_document_fail_on_wrong_role(self):
            self.mock_get_role.return_value = known_control_types.index("Invalid")
            self.assertRaises(AttributeError, lambda: self.info.document)

        @mock.patch.object(AtspiDocument, 'get_locale')
        def test_document_get_locale_success(self, mock_get_locale):
            mock_get_locale.return_value = b"C"
            self.assertEqual(self.info.document_get_locale(), u"C")


if __name__ == "__main__":
    unittest.main()
