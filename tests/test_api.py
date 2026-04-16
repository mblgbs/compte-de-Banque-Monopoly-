import json
import threading
import time
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer

from api import MonopolyRequestHandler
from banque_monopoly import BanqueMonopoly


class TestApiMonopoly(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        MonopolyRequestHandler.banque = BanqueMonopoly()
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), MonopolyRequestHandler)
        cls.host, cls.port = cls.server.server_address
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        time.sleep(0.05)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=1)

    def request(self, method, path, payload=None):
        conn = HTTPConnection(self.host, self.port, timeout=2)
        headers = {"Content-Type": "application/json"}
        body = json.dumps(payload) if payload is not None else None
        conn.request(method, path, body=body, headers=headers)
        response = conn.getresponse()
        raw = response.read().decode("utf-8")
        conn.close()
        return response.status, json.loads(raw)

    def test_health(self):
        status, data = self.request("GET", "/health")
        self.assertEqual(status, 200)
        self.assertEqual(data["status"], "ok")

    def test_create_and_list_accounts(self):
        status, created = self.request("POST", "/comptes", {"nom": "Alice", "solde_initial": 1500})
        self.assertEqual(status, 201)
        self.assertEqual(created["nom"], "Alice")

        status, listing = self.request("GET", "/comptes")
        self.assertEqual(status, 200)
        self.assertGreaterEqual(len(listing["comptes"]), 1)

    def test_transfer(self):
        _, a = self.request("POST", "/comptes", {"nom": "A", "solde_initial": 1000})
        _, b = self.request("POST", "/comptes", {"nom": "B", "solde_initial": 1000})

        status, result = self.request(
            "POST",
            "/transferts",
            {"source_id": a["id"], "destination_id": b["id"], "montant": 300},
        )

        self.assertEqual(status, 200)
        self.assertEqual(result["source"]["solde"], 700)
        self.assertEqual(result["destination"]["solde"], 1300)


if __name__ == "__main__":
    unittest.main()
