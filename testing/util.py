import io
import re
from xml.etree import ElementTree

# --------------------------------------------------------------------
# Taken from Python 3.8's ElementTree.py.


def canonicalize(xml_data=None, *, out=None, from_file=None, **options):
    """Convert XML to its C14N 2.0 serialised form.

    If *out* is provided, it must be a file or file-like object that receives
    the serialised canonical XML output (text, not bytes) through its ``.write()``
    method.  To write to a file, open it in text mode with encoding "utf-8".
    If *out* is not provided, this function returns the output as text string.

    Either *xml_data* (an XML string) or *from_file* (a file path or
    file-like object) must be provided as input.

    The configuration options are the same as for the ``C14NWriterTarget``.
    """
    if xml_data is None and from_file is None:
        raise ValueError("Either 'xml_data' or 'from_file' must be provided as input")
    sio = None
    if out is None:
        sio = out = io.StringIO()

    parser = ElementTree.XMLParser(target=C14NWriterTarget(out.write, **options))

    if xml_data is not None:
        parser.feed(xml_data)
        parser.close()
    elif from_file is not None:
        ElementTree.parse(from_file, parser=parser)

    return sio.getvalue() if sio is not None else None


_looks_like_prefix_name = re.compile(r"^\w+:\w+$", re.UNICODE).match


class C14NWriterTarget:
    """
    Canonicalization writer target for the XMLParser.

    Serialises parse events to XML C14N 2.0.

    The *write* function is used for writing out the resulting data stream
    as text (not bytes).  To write to a file, open it in text mode with encoding
    "utf-8" and pass its ``.write`` method.

    Configuration options:

    - *with_comments*: set to true to include comments
    - *strip_text*: set to true to strip whitespace before and after text content
    - *rewrite_prefixes*: set to true to replace namespace prefixes by "n{number}"
    - *qname_aware_tags*: a set of qname aware tag names in which prefixes
                          should be replaced in text content
    - *qname_aware_attrs*: a set of qname aware attribute names in which prefixes
                           should be replaced in text content
    - *exclude_attrs*: a set of attribute names that should not be serialised
    - *exclude_tags*: a set of tag names that should not be serialised
    """

    def __init__(
        self,
        write,
        *,
        with_comments=False,
        strip_text=False,
        rewrite_prefixes=False,
        qname_aware_tags=None,
        qname_aware_attrs=None,
        exclude_attrs=None,
        exclude_tags=None,
    ):
        self._write = write
        self._data = []
        self._with_comments = with_comments
        self._strip_text = strip_text
        self._exclude_attrs = set(exclude_attrs) if exclude_attrs else None
        self._exclude_tags = set(exclude_tags) if exclude_tags else None

        self._rewrite_prefixes = rewrite_prefixes
        if qname_aware_tags:
            self._qname_aware_tags = set(qname_aware_tags)
        else:
            self._qname_aware_tags = None
        if qname_aware_attrs:
            self._find_qname_aware_attrs = set(qname_aware_attrs).intersection
        else:
            self._find_qname_aware_attrs = None

        # Stack with globally and newly declared namespaces as (uri, prefix) pairs.
        self._declared_ns_stack = [
            [
                ("http://www.w3.org/XML/1998/namespace", "xml"),
            ]
        ]
        # Stack with user declared namespace prefixes as (uri, prefix) pairs.
        self._ns_stack = []
        if not rewrite_prefixes:
            # this must not be separated from ElementTree
            self._ns_stack.append(list(ElementTree._namespace_map.items()))
        self._ns_stack.append([])
        self._prefix_map = {}
        self._preserve_space = [False]
        self._pending_start = None
        self._root_seen = False
        self._root_done = False
        self._ignored_depth = 0

    def _iter_namespaces(self, ns_stack, _reversed=reversed):
        for namespaces in _reversed(ns_stack):
            if namespaces:  # almost no element declares new namespaces
                yield from namespaces

    def _resolve_prefix_name(self, prefixed_name):
        prefix, name = prefixed_name.split(":", 1)
        for uri, p in self._iter_namespaces(self._ns_stack):
            if p == prefix:
                return f"{{{uri}}}{name}"
        raise ValueError(
            f'Prefix {prefix} of QName "{prefixed_name}" is not declared in scope'
        )

    def _qname(self, qname, uri=None):
        if uri is None:
            uri, tag = qname[1:].rsplit("}", 1) if qname[:1] == "{" else ("", qname)
        else:
            tag = qname

        prefixes_seen = set()
        for u, prefix in self._iter_namespaces(self._declared_ns_stack):
            if u == uri and prefix not in prefixes_seen:
                return f"{prefix}:{tag}" if prefix else tag, tag, uri
            prefixes_seen.add(prefix)

        # Not declared yet => add new declaration.
        if self._rewrite_prefixes:
            if uri in self._prefix_map:
                prefix = self._prefix_map[uri]
            else:
                prefix = self._prefix_map[uri] = f"n{len(self._prefix_map)}"
            self._declared_ns_stack[-1].append((uri, prefix))
            return f"{prefix}:{tag}", tag, uri

        if not uri and "" not in prefixes_seen:
            # No default namespace declared => no prefix needed.
            return tag, tag, uri

        for u, prefix in self._iter_namespaces(self._ns_stack):
            if u == uri:
                self._declared_ns_stack[-1].append((uri, prefix))
                return f"{prefix}:{tag}" if prefix else tag, tag, uri

        raise ValueError(f'Namespace "{uri}" is not declared in scope')

    def data(self, data):
        if not self._ignored_depth:
            self._data.append(data)

    def _flush(self, _join_text="".join):
        data = _join_text(self._data)
        del self._data[:]
        if self._strip_text and not self._preserve_space[-1]:
            data = data.strip()
        if self._pending_start is not None:
            args, self._pending_start = self._pending_start, None
            qname_text = data if data and _looks_like_prefix_name(data) else None
            self._start(*args, qname_text)
            if qname_text is not None:
                return
        if data and self._root_seen:
            self._write(_escape_cdata_c14n(data))

    def start_ns(self, prefix, uri):
        if self._ignored_depth:
            return
        # we may have to resolve qnames in text content
        if self._data:
            self._flush()
        self._ns_stack[-1].append((uri, prefix))

    def start(self, tag, attrs):
        if self._exclude_tags is not None and (
            self._ignored_depth or tag in self._exclude_tags
        ):
            self._ignored_depth += 1
            return
        if self._data:
            self._flush()

        new_namespaces = []
        self._declared_ns_stack.append(new_namespaces)

        if self._qname_aware_tags is not None and tag in self._qname_aware_tags:
            # Need to parse text first to see if it requires a prefix declaration.
            self._pending_start = (tag, attrs, new_namespaces)
            return
        self._start(tag, attrs, new_namespaces)

    def _start(self, tag, attrs, new_namespaces, qname_text=None):
        if self._exclude_attrs is not None and attrs:
            attrs = {k: v for k, v in attrs.items() if k not in self._exclude_attrs}

        qnames = {tag, *attrs}
        resolved_names = {}

        # Resolve prefixes in attribute and tag text.
        if qname_text is not None:
            qname = resolved_names[qname_text] = self._resolve_prefix_name(qname_text)
            qnames.add(qname)
        if self._find_qname_aware_attrs is not None and attrs:
            qattrs = self._find_qname_aware_attrs(attrs)
            if qattrs:
                for attr_name in qattrs:
                    value = attrs[attr_name]
                    if _looks_like_prefix_name(value):
                        qname = resolved_names[value] = self._resolve_prefix_name(value)
                        qnames.add(qname)
            else:
                qattrs = None
        else:
            qattrs = None

        # Assign prefixes in lexicographical order of used URIs.
        parse_qname = self._qname
        parsed_qnames = {
            n: parse_qname(n) for n in sorted(qnames, key=lambda n: n.split("}", 1))
        }

        # Write namespace declarations in prefix order ...
        if new_namespaces:
            attr_list = [
                ("xmlns:" + prefix if prefix else "xmlns", uri)
                for uri, prefix in new_namespaces
            ]
            attr_list.sort()
        else:
            # almost always empty
            attr_list = []

        # ... followed by attributes in URI+name order
        if attrs:
            for k, v in sorted(attrs.items()):
                if qattrs is not None and k in qattrs and v in resolved_names:
                    v = parsed_qnames[resolved_names[v]][0]
                attr_qname, attr_name, uri = parsed_qnames[k]
                # No prefix for attributes in default ('') namespace.
                attr_list.append((attr_qname if uri else attr_name, v))

        # Honour xml:space attributes.
        space_behaviour = attrs.get("{http://www.w3.org/XML/1998/namespace}space")
        self._preserve_space.append(
            space_behaviour == "preserve"
            if space_behaviour
            else self._preserve_space[-1]
        )

        # Write the tag.
        write = self._write
        write("<" + parsed_qnames[tag][0])
        if attr_list:
            write("".join([f' {k}="{_escape_attrib_c14n(v)}"' for k, v in attr_list]))
        write(">")

        # Write the resolved qname text content.
        if qname_text is not None:
            write(_escape_cdata_c14n(parsed_qnames[resolved_names[qname_text]][0]))

        self._root_seen = True
        self._ns_stack.append([])

    def end(self, tag):
        if self._ignored_depth:
            self._ignored_depth -= 1
            return
        if self._data:
            self._flush()
        self._write(f"</{self._qname(tag)[0]}>")
        self._preserve_space.pop()
        self._root_done = len(self._preserve_space) == 1
        self._declared_ns_stack.pop()
        self._ns_stack.pop()

    def comment(self, text):
        if not self._with_comments:
            return
        if self._ignored_depth:
            return
        if self._root_done:
            self._write("\n")
        elif self._root_seen and self._data:
            self._flush()
        self._write(f"<!--{_escape_cdata_c14n(text)}-->")
        if not self._root_seen:
            self._write("\n")

    def pi(self, target, data):
        if self._ignored_depth:
            return
        if self._root_done:
            self._write("\n")
        elif self._root_seen and self._data:
            self._flush()
        self._write(
            f"<?{target} {_escape_cdata_c14n(data)}?>" if data else f"<?{target}?>"
        )
        if not self._root_seen:
            self._write("\n")


def _escape_cdata_c14n(text):
    # escape character data
    try:
        # it's worth avoiding do-nothing calls for strings that are
        # shorter than 500 character, or so.  assume that's, by far,
        # the most common case in most applications.
        if "&" in text:
            text = text.replace("&", "&amp;")
        if "<" in text:
            text = text.replace("<", "&lt;")
        if ">" in text:
            text = text.replace(">", "&gt;")
        if "\r" in text:
            text = text.replace("\r", "&#xD;")
        return text
    except (TypeError, AttributeError):
        ElementTree._raise_serialization_error(text)


def _escape_attrib_c14n(text):
    # escape attribute value
    try:
        if "&" in text:
            text = text.replace("&", "&amp;")
        if "<" in text:
            text = text.replace("<", "&lt;")
        if '"' in text:
            text = text.replace('"', "&quot;")
        if "\t" in text:
            text = text.replace("\t", "&#x9;")
        if "\n" in text:
            text = text.replace("\n", "&#xA;")
        if "\r" in text:
            text = text.replace("\r", "&#xD;")
        return text
    except (TypeError, AttributeError):
        ElementTree._raise_serialization_error(text)
