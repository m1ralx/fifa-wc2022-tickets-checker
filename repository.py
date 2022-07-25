import os
from typing import List, Tuple
from datetime import datetime

import ydb

from models import Match
from encoding import decode_matches, encode_matches
from timestamp import get_timestamp


class MatchesRepository:
    def __init__(self) -> None:
        driver = ydb.Driver(
            endpoint=os.getenv('YDB_ENDPOINT'), 
            database=os.getenv('YDB_DATABASE'),
        )
        driver.wait(fail_fast=True, timeout=30)
        self.pool = ydb.SessionPool(driver)


    def get_current_matches(self) -> Tuple[int, List[Match]]:
        result = self.pool.retry_operation_sync(self._select_latest_matches)
        if len(result) == 0 or len(result[0].rows) == 0:
            return 0, []
        data = result[0].rows[0].data
        timestamp = result[0].rows[0].timestamp
        if not data:
            return 0, []
        return timestamp, decode_matches(data)


    def store_matches(self, dt: datetime, matches: List[Match]) -> None:
        return self.pool.retry_operation_sync(self._upsert_matches(dt, matches))


    @staticmethod
    def _select_latest_matches(session):
        return session.transaction().execute(
            """
            $latest_ts = SELECT MAX(`timestamp`) FROM results;
            
            SELECT 
                CAST(`timestamp` AS Int64) AS `timestamp`,
                data
            FROM results 
            WHERE `timestamp` = $latest_ts;
            """,
            commit_tx=True,
            settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2),
        )

    @staticmethod
    def _upsert_matches(dt: datetime, matches: List[Match]):
        query =  """     
            DECLARE $timestamp AS TIMESTAMP;
            DECLARE $matches AS Utf8;

            UPSERT INTO results (`timestamp`, data)
            VALUES ($timestamp, CAST($matches AS JSON)); 
        """
        def callee(session: ydb.Session):
            tx = session.transaction(ydb.SerializableReadWrite()).begin()
            prepared_query = session.prepare(query)
            return tx.execute(
                prepared_query,
                parameters={
                    '$timestamp': get_timestamp(dt),
                    '$matches': encode_matches(matches),
                },
                commit_tx=True,
                settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2),
            )

        return callee
