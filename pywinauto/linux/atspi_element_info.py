from .atspi_objects import AtspiRect, _AtspiCoordType, AtspiAccessible, RECT, known_control_types, AtspiComponent, \
    AtspiStateSet
from .atspi_objects import AtspiDocument
from ..element_info import ElementInfo


class AtspiElementInfo(ElementInfo):

    """Wrapper for window handler"""
    atspi_accessible = AtspiAccessible()

    def __init__(self, handle=None):
        """Create element by handle (default is root element)"""
        if handle is None:
            self._handle = self.atspi_accessible.get_desktop(0)
        else:
            self._handle = handle

    def __get_elements(self, root, tree):
        tree.append(root)
        for el in root.children():
            self.__get_elements(el, tree)

    def __eq__(self, other):
        if self.class_name == "application":
            return self.process_id == other.process_id
        return self.rectangle == other.rectangle

    @property
    def handle(self):
        """Return the handle of the window"""
        return self._handle

    @property
    def name(self):
        """Return the text of the window"""
        return self.atspi_accessible.get_name(self._handle, None).decode(encoding='UTF-8')

    @property
    def control_id(self):
        """Return the ID of the window"""
        return self.atspi_accessible.get_role(self._handle, None)

    @property
    def process_id(self):
        """Return the ID of process that controls this window"""
        return self.atspi_accessible.get_process_id(self._handle, None)

    @property
    def class_name(self):
        """Return the class name of the element"""
        return self.atspi_accessible.get_role_name(self._handle, None).decode(encoding='UTF-8')

    @property
    def rich_text(self):
        """Return the text of the element"""
        return self.name

    @property
    def control_type(self):
        """Return the class name of the element"""
        role_id = self.atspi_accessible.get_role(self._handle, None)
        return known_control_types[role_id]

    @property
    def parent(self):
        """Return the parent of the element"""
        if self == AtspiElementInfo():
            return None
        return AtspiElementInfo(self.atspi_accessible.get_parent(self._handle, None))

    def children(self, **kwargs):
        """Return children of the element"""
        len = self.atspi_accessible.get_child_count(self._handle, None)
        childrens = []
        for i in range(len):
            childrens.append(self.atspi_accessible.get_child_at_index(self._handle, i, None))
        return [AtspiElementInfo(ch) for ch in childrens]

    @property
    def component(self):
        component = self.atspi_accessible.get_component(self._handle)
        return AtspiComponent(component)

    def document_get_locale(self):
        """Return the document's content locale"""
        return self.document.get_locale().decode(encoding='UTF-8')

    def descendants(self, **kwargs):
        """Return descendants of the element"""
        tree = []
        for obj in self.children():
            self.__get_elements(obj, tree)
        return tree

    def description(self):
        return self.atspi_accessible.get_description(self._handle, None).decode(encoding='UTF-8')

    def framework_id(self):
        return self.atspi_accessible.get_toolkit_version(self._handle, None).decode(encoding='UTF-8')

    def framework_name(self):
        return self.atspi_accessible.get_toolkit_name(self._handle, None).decode(encoding='UTF-8')

    def atspi_version(self):
        return self.atspi_accessible.get_atspi_version(self._handle, None).decode(encoding='UTF-8')

    def get_layer(self):
        """Return rectangle of element"""
        if self.control_type == "Application":
            return self.children()[0].get_layer()
        return self.component.get_layer()

    def get_order(self):
        if self.control_type == "Application":
            return self.children()[0].get_order()
        return self.component.get_mdi_x_order()

    def get_state_set(self):
        return AtspiStateSet(self.atspi_accessible.get_state_set(self.handle))

    @property
    def rectangle(self):
        """Return rectangle of element"""
        if self.control_type == "Application":
            # Application object have`t rectangle. It`s just a fake container which contain base application
            # info such as process ID, window name etc. Will return application frame rectangle
            return self.children()[0].rectangle
        return self.component.get_rectangle(coord_type="screen")

    @property
    def document(self):
        """Return AtspiDocument interface"""
        if self.control_type == "Document_frame":
            document = self.atspi_accessible.get_document(self._handle)
            return AtspiDocument(document)
        else:
            raise AttributeError
