import http.client
import importlib.util
from pathlib import Path
import threading
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "server.py"
spec = importlib.util.spec_from_file_location("goreecloud_contacts_web_server", SOURCE)
server_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server_module)

class StaticWebTests(unittest.TestCase):
    def setUp(self):
        self.server = server_module.ThreadingHTTPServer(("127.0.0.1", 0),
                                                         server_module.ContactsHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    def request(self, method, path):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=2)
        connection.request(method, path)
        response = connection.getresponse()
        payload = response.read()
        result = (response.status, dict(response.getheaders()), payload)
        connection.close()
        return result

    def test_whitelisted_assets_secure_headers_and_no_network_calls(self):
        for path in ("/", "/index.html", "/style.css", "/main.mjs",
                     "/model.mjs", "/store.mjs", "/gc-ui/tokens.css",
                     "/assets/goreecloud-logo.svg"):
            status, headers, body = self.request("GET", path)
            self.assertEqual(status, 200, path)
            self.assertTrue(body)
            self.assertIn("connect-src 'none'", headers["Content-Security-Policy"])
            self.assertEqual(headers["X-Frame-Options"], "DENY")
            self.assertEqual(headers["X-Content-Type-Options"], "nosniff")
            self.assertEqual(headers["Cache-Control"], "no-store")
        for path in ("/.git/config", "/package.json", "/web/", "/shared/fixtures/contacts-v1.json",
                     "/../../etc/passwd", "/../index.html", "/server.py", "/gc-ui/LICENSE"):
            self.assertEqual(self.request("GET", path)[0], 404, path)
        self.assertEqual(self.request("POST", "/")[0], 405)
        self.assertEqual(self.request("HEAD", "/index.html")[0], 200)

    def test_user_provided_query_does_not_leak_in_html(self):
        result=self.request("GET", "/index.html?contact=%3Csecret%3E")
        self.assertEqual(result[0], 200)
        self.assertNotIn(b"<secret>", result[2])
        html=result[2].decode("utf-8")
        self.assertIn('type="module" src="./main.mjs"',html)
        self.assertIn("Your contacts stay yours.",html)
        self.assertNotIn("https://", html)

if __name__ == "__main__":
    unittest.main()
