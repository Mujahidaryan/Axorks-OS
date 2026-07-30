import pytest
from uuid import uuid4
from src.modules.marketing.service import MarketingService
from src.modules.marketing.schemas import CampaignCreate, ContentItemCreate, EmailCampaignCreate

@pytest.mark.asyncio
async def test_marketing_service_flow(db):
    svc = MarketingService(db)
    org_id = uuid4()
    ws_id = uuid4()
    user_id = uuid4()

    # 1. Create Campaign
    c_data = CampaignCreate(name="Summer Campaign 2026", type="email", budget=10000)
    campaign = await svc.create_campaign(org_id, ws_id, user_id, c_data)
    assert campaign.name == "Summer Campaign 2026"
    assert campaign.organization_id == org_id

    # 2. List Campaigns
    campaigns = await svc.list_campaigns(org_id)
    assert len(campaigns) == 1

    # 3. Create Content Item
    ci_data = ContentItemCreate(title="Launch Post", content_type="post", platform="linkedin", campaign_id=campaign.id)
    content_item = await svc.create_content_item(org_id, ci_data)
    assert content_item.title == "Launch Post"

    # 4. Create Email Campaign
    ec_data = EmailCampaignCreate(campaign_id=campaign.id, subject="Special Offer", from_name="Axorks")
    email_campaign = await svc.create_email_campaign(org_id, ec_data)
    assert email_campaign.subject == "Special Offer"
