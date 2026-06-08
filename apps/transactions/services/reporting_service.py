from django.db import connection

from apps.clients.models import Client


class ReportingService:
    @staticmethod
    def get_montant_retirable(*, client_id: int) -> int:
        with connection.cursor() as cursor:
            cursor.execute("SELECT transactions_get_montant_retirable(%s)", [client_id])
            row = cursor.fetchone()
        return int(row[0] or 0)

    @classmethod
    def get_client_financial_summary(cls, *, client_id: int) -> dict:
        client = Client.objects.select_related("agent").get(id=client_id)
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    total_credit_client,
                    total_retraits,
                    montant_retirable
                FROM v_client_montant_retirable
                WHERE client_id = %s
                """,
                [client_id],
            )
            row = cursor.fetchone()

        if row is None:
            total_credit_client = 0
            total_retraits = 0
            montant_retirable = 0
        else:
            total_credit_client, total_retraits, montant_retirable = [int(value or 0) for value in row]

        return {
            "client_id": client.id,
            "client_code": client.code,
            "client_nom_complet": f"{client.nom} {client.prenom}".strip(),
            "agent_code": client.agent.code,
            "montant_retirable": montant_retirable,
            "total_credit_client": total_credit_client,
            "total_retraits": total_retraits,
        }

    @staticmethod
    def get_portfolio_retirable_total(*, agent_id: int | None = None) -> int:
        sql = "SELECT COALESCE(SUM(montant_retirable), 0) FROM v_client_montant_retirable"
        params = []
        if agent_id is not None:
            sql += " WHERE agent_id = %s"
            params.append(agent_id)

        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            row = cursor.fetchone()
        return int(row[0] or 0)

    @staticmethod
    def list_agent_commissions(*, agent_id: int | None = None) -> list[dict]:
        sql = """
            SELECT agent_id, agent_code, total_commissions, nb_commissions
            FROM v_agent_commissions
        """
        params = []
        if agent_id is not None:
            sql += " WHERE agent_id = %s"
            params.append(agent_id)
        sql += " ORDER BY total_commissions DESC, agent_code ASC"

        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchall()

        return [
            {
                "agent_id": int(row[0]),
                "agent_code": row[1],
                "total_commissions": int(row[2] or 0),
                "nb_commissions": int(row[3] or 0),
            }
            for row in rows
        ]

    @staticmethod
    def list_client_retirable_rows(*, agent_id: int | None = None, limit: int | None = None) -> list[dict]:
        sql = """
            SELECT
                client_id,
                agent_id,
                client_code,
                client_nom_complet,
                total_credit_client,
                total_retraits,
                montant_retirable
            FROM v_client_montant_retirable
        """
        params = []
        if agent_id is not None:
            sql += " WHERE agent_id = %s"
            params.append(agent_id)
        sql += " ORDER BY montant_retirable DESC, client_code ASC"
        if limit is not None:
            sql += " LIMIT %s"
            params.append(limit)

        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchall()

        return [
            {
                "client_id": int(row[0]),
                "agent_id": int(row[1]),
                "client_code": row[2],
                "client_nom_complet": row[3],
                "total_credit_client": int(row[4] or 0),
                "total_retraits": int(row[5] or 0),
                "montant_retirable": int(row[6] or 0),
            }
            for row in rows
        ]
