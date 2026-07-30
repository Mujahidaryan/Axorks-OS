import pytest
from uuid import uuid4
from src.modules.integrations.service import IntegrationService
from src.modules.integrations.schemas import IntegrationConnect, WebhookCreate

@pytest.mark.asyncio
async def test_integrations_flow(db):
    svc = IntegrationService(db)
    org_id = uuid4()

    # 1. Catalog
    cat = svc.get_catalog()
    assert "github" in cat
    assert "slack" in cat

    # 2. Connect Integration
    conn_data = IntegrationConnect(provider="github", access_token="ghp_mocktoken123", account_identifier="axorks-org")
    integration = await svc.connect(org_id, conn_data)
    assert integration.provider == "github"
    assert integration.status == "connected"

    # 3. List Connected
    connected = await svc.list_connected(org_id)
    assert len(connected) == 1

    # 4. Create Webhook
    wh_data = WebhookCreate(url="https://api.axorks.com/webhooks/github", events=["push", "pull_request"])
    webhook = await svc.create_webhook(org_id, wh_data)
    assert webhook.url == "https://api.axorks.com/webhooks/github"

    # 5. Disconnect
    await svc.disconnect(org_id, "github")
    connected_after = await svc.list_connected(org_id)
    assert len(connected_after) == 0
