from __future__ import annotations

import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from banque_monopoly import (
    BanqueMonopoly,
    CompteIntrouvableError,
    SoldeInsuffisantError,
    compte_en_dict,
)
from save_service_client import SaveServiceError, load_bank_state, save_bank_state


class MonopolyRequestHandler(BaseHTTPRequestHandler):
    banque = BanqueMonopoly()
    auth_enabled = os.getenv("SERVICE_AUTH_ENABLED", "false").lower() == "true"
    franceconnect_base_url = os.getenv("FRANCECONNECT_BASE_URL", "http://127.0.0.1:8001").rstrip("/")
    auth_timeout_seconds = float(os.getenv("AUTH_REQUEST_TIMEOUT_SECONDS", "2.5"))

    def _persist_state(self) -> None:
        try:
            save_bank_state(self.banque.export_state())
        except SaveServiceError as err:
            print(f"[save-service] persist failed: {err}")

    def _read_json(self) -> dict:
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return {}

        raw = self.rfile.read(content_length)
        return json.loads(raw.decode("utf-8"))

    def _send_json(self, status: int, payload: dict | list) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _handle_error(self, err: Exception) -> None:
        if isinstance(err, CompteIntrouvableError):
            self._send_json(HTTPStatus.NOT_FOUND, {"error": str(err)})
        elif isinstance(err, SoldeInsuffisantError):
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(err)})
        elif isinstance(err, (ValueError, json.JSONDecodeError)):
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(err)})
        else:
            self._send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "Erreur interne"})

    def _require_auth(self) -> bool:
        if not self.auth_enabled:
            return True
        auth_header = self.headers.get("Authorization", "")
        if not auth_header.lower().startswith("bearer "):
            self._send_json(HTTPStatus.UNAUTHORIZED, {"error": "Authentication required"})
            return False
        token = auth_header[7:].strip()
        if not token:
            self._send_json(HTTPStatus.UNAUTHORIZED, {"error": "Authentication required"})
            return False

        request = Request(
            f"{self.franceconnect_base_url}/auth/introspect",
            headers={"Authorization": f"Bearer {token}"},
            method="GET",
        )
        try:
            with urlopen(request, timeout=self.auth_timeout_seconds) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception:
            self._send_json(HTTPStatus.SERVICE_UNAVAILABLE, {"error": "Auth provider unavailable"})
            return False

        if not payload.get("active"):
            self._send_json(HTTPStatus.UNAUTHORIZED, {"error": "Invalid token"})
            return False
        return True

    def do_GET(self) -> None:  # noqa: N802
        try:
            path = urlparse(self.path).path
            if path == "/health":
                self._send_json(HTTPStatus.OK, {"status": "ok"})
                return
            if not self._require_auth():
                return
            if path == "/comptes":
                comptes = [compte_en_dict(c) for c in self.banque.lister_comptes()]
                self._send_json(HTTPStatus.OK, {"comptes": comptes})
                return
            if path.startswith("/comptes/"):
                compte_id = int(path.split("/")[2])
                compte = self.banque.obtenir_compte(compte_id)
                self._send_json(HTTPStatus.OK, compte_en_dict(compte))
                return
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "Route introuvable"})
        except Exception as err:  # pragma: no cover - handled by tests via behavior
            self._handle_error(err)

    def do_POST(self) -> None:  # noqa: N802
        try:
            path = urlparse(self.path).path
            payload = self._read_json()
            if not self._require_auth():
                return

            if path == "/comptes":
                nom = payload["nom"]
                solde_initial = int(payload.get("solde_initial", 1500))
                compte = self.banque.creer_compte(nom, solde_initial)
                self._persist_state()
                self._send_json(HTTPStatus.CREATED, compte_en_dict(compte))
                return

            if path.startswith("/comptes/") and path.endswith("/depot"):
                compte_id = int(path.split("/")[2])
                montant = int(payload["montant"])
                compte = self.banque.depot(compte_id, montant)
                self._persist_state()
                self._send_json(HTTPStatus.OK, compte_en_dict(compte))
                return

            if path.startswith("/comptes/") and path.endswith("/retrait"):
                compte_id = int(path.split("/")[2])
                montant = int(payload["montant"])
                compte = self.banque.retrait(compte_id, montant)
                self._persist_state()
                self._send_json(HTTPStatus.OK, compte_en_dict(compte))
                return

            if path == "/transferts":
                source_id = int(payload["source_id"])
                destination_id = int(payload["destination_id"])
                montant = int(payload["montant"])
                self.banque.transfert(source_id, destination_id, montant)
                self._persist_state()
                self._send_json(
                    HTTPStatus.OK,
                    {
                        "message": "Transfert effectué",
                        "source": compte_en_dict(self.banque.obtenir_compte(source_id)),
                        "destination": compte_en_dict(self.banque.obtenir_compte(destination_id)),
                    },
                )
                return

            self._send_json(HTTPStatus.NOT_FOUND, {"error": "Route introuvable"})
        except Exception as err:  # pragma: no cover - handled by tests via behavior
            self._handle_error(err)


def run_server(host: str = "0.0.0.0", port: int = 8002) -> None:
    try:
        saved = load_bank_state()
        if saved:
            MonopolyRequestHandler.banque.import_state(saved)
            print("[save-service] bank state loaded")
    except SaveServiceError as err:
        print(f"[save-service] unavailable at startup, in-memory fallback: {err}")
    server = ThreadingHTTPServer((host, port), MonopolyRequestHandler)
    print(f"API Monopoly disponible sur http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
