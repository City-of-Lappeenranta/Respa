import logging

import requests
from http.client import IncompleteRead
from lxml import etree
from requests.packages.urllib3.util.retry import Retry
from requests.auth import HTTPBasicAuth
from requests.adapters import HTTPAdapter

from .xml import NAMESPACES

SOAP_ENVELOPE_TAG = b'<Envelope xmlns="http://schemas.xmlsoap.org/soap/envelope/">'


class SoapFault(Exception):
    def __init__(self, fault_code, fault_string, detail_element=None):
        self.code = fault_code
        self.text = fault_string
        self.detail_element = (detail_element if (detail_element is not None) else None)
        self.detail_text = (
            etree.tostring(self.detail_element, pretty_print=True)
            if (self.detail_element is not None)
            else None
        )
        super(SoapFault, self).__init__("%s (%s)" % (self.text, self.code))

    @classmethod
    def from_xml(cls, fault_element):
        fault_code_el = fault_element.find("faultcode")
        fault_text_el = fault_element.find("faultstring")
        return cls(
            fault_code=(fault_code_el.text if (fault_code_el is not None) else None),
            fault_string=(fault_text_el.text if (fault_text_el is not None) else None),
            detail_element=fault_element.find("detail")
        )


class ExchangeSession(requests.Session):
    """
    Encapsulates an NTLM authenticated requests session with special capabilities to do SOAP requests.
    """

    encoding = "UTF-8"

    def __init__(self, url, username, password):
        super(ExchangeSession, self).__init__()
        self.url = url
        # Ntml authentication not supported by O365, so use basic authentication
        self.auth = HTTPBasicAuth(username, password)
        self.log = logging.getLogger("ExchangeSession")

        # Retry the requests a couple of times in case of a connection error.
        num_retries = 3
        retry = Retry(
            total=num_retries,
            connect=num_retries,
            read=0,
            status=0,
            backoff_factor=0.3,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.mount('http://', adapter)
        self.mount('https://', adapter)

    def _prepare_soap(self, request):
        envelope = request.envelop()
        body = etree.tostring(envelope, pretty_print=True, encoding=self.encoding)
        self.log.debug(
            "SENDING: %s",
            body.decode(self.encoding)
        )
        headers = {
            "Accept": "text/xml",
            "Content-type": "text/xml; charset=%s" % self.encoding
        }
        return dict(data=body, headers=headers, auth=self.auth)

    def soap(self, request, timeout=10):
        """
        Send an EWSRequest by SOAP.

        :type request: respa_exchange.base.EWSRequest
        :param timeout: request timeout (see `requests` docs)
        :type timeout: float|None|tuple[float, float]
        :rtype: lxml.etree.Element
        """

        resp = self.post(
            self.url, timeout=timeout, **self._prepare_soap(request)
        )
        if resp.status_code == 500:
            try:
                self._process_soap_response(resp.content)
            except SoapFault:
                raise
        resp.raise_for_status()
        return self._process_soap_response(resp.content)

    def soap_stream(self, request, timeout=10):
        """
        Send an EWSRequest by SOAP and stream the response.
        """
        resp = self.post(self.url, timeout=timeout, stream=True, **self._prepare_soap(request))
        """
        In the original implementation, data from iter_content was sometimes incomplete, resulting in
        parsing failure in _process_soap_response.
        We want to wait that we get the closing tag, </Envelope>, before we parse the response.

        urllib3 that requests uses may sometimes throw http.client.IncompleteRead
        We want to catch it so that logs are not filled with the stacktrace.
        """
        try:
            resp_data = b''
            for data in resp.iter_content(chunk_size=None):
                data = data.strip()
                if not data:
                    continue
                resp_data += data
                if resp_data.endswith(b'</Envelope>'):
                    # Only yield if this was the end of the current response
                    temp_data = resp_data
                    # Clear resp_data and wait for new message
                    resp_data = b''
                    yield self._process_soap_response(temp_data)
        except IncompleteRead as exception:
            raise Exception('Incomplete read from urllib3')

    def _process_soap_response(self, content):
        if content.count(SOAP_ENVELOPE_TAG) > 1:
            self.log.debug('Multiple envelopes in response %r, using `recover` mode for parsing.', content)
            recover = True
        else:
            recover = False

        tree = etree.XML(content, parser=etree.XMLParser(recover=recover))

        self.log.debug(
            "RECEIVED: %s",
            etree.tostring(tree, pretty_print=True, encoding=self.encoding).decode(self.encoding)
        )
        fault_nodes = tree.xpath(u'//s:Fault', namespaces=NAMESPACES)
        if fault_nodes:
            raise SoapFault.from_xml(fault_nodes[0])
        return tree
