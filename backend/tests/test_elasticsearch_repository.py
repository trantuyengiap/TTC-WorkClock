from app.services.elasticsearch.repository import AttendanceElasticRepository


class DummyClient:
    def search(self, index: str, body: dict):
        return {'hits': {'hits': [], 'total': {'value': 0}}, 'aggregations': {'users': {'buckets': []}, 'present_users': {'value': 0}, 'event_outcomes': {'buckets': []}}}

    class cluster:
        @staticmethod
        def health() -> dict:
            return {'status': 'green'}


def test_recent_events_query_uses_hikvision_mapping() -> None:
    repo = AttendanceElasticRepository(client=DummyClient())
    query = repo.build_recent_events_query(minutes=10, size=25, sort_order='desc')
    assert query['size'] == 25
    assert query['sort'][0]['@timestamp']['order'] == 'desc'
    assert query['query']['bool']['filter'][1]['exists']['field'] == 'hikvision.AccessControllerEvent.employeeNoString'
