from django.urls import include, path



from apps.analytics.urls import admin_urlpatterns as command_center_urls

from apps.common import push_urls as common_push_urls

from apps.creator_hub.urls import admin_urlpatterns as creator_admin_urls

from apps.email_growth.urls import admin_urlpatterns as email_admin_urls

from apps.experiments.urls import admin_urlpatterns as experiments_admin_urls

from apps.marketplace.urls import admin_urlpatterns as marketplace_admin_urls

from apps.monetization.urls import admin_urlpatterns as monetization_admin_urls

from apps.referrals.urls import admin_urlpatterns as referrals_admin_urls

from apps.subscriptions.urls import billing_urlpatterns

from apps.tool_intelligence.urls import tool_scores_urlpatterns

from apps.workflows.urls import admin_urlpatterns as workflows_admin_urls



urlpatterns = [

    path("auth/", include("apps.users.urls")),

    path("", include("apps.tools_registry.urls")),

    path("favorites/", include("apps.favorites.urls")),

    path("history/", include("apps.history.urls")),

    path("subscriptions/", include("apps.subscriptions.urls")),

    path("billing/", include(billing_urlpatterns)),

    path("blog/", include("apps.blog.urls")),

    path("analytics/", include("apps.analytics.urls")),

    path("admin/", include("apps.admin_api.urls")),

    path("admin/content/", include("apps.content_factory.urls")),

    path("admin/autopilot/", include("apps.content_factory.autopilot_urls")),

    path("admin/tool-factory/", include("apps.tool_factory.urls")),

    path("admin/gsc/", include("apps.search_console.urls")),

    path("admin/seo/", include("apps.seo_optimizer.urls")),

    path("admin/keywords/", include("apps.keywords.urls")),

    path("admin/opportunities/", include("apps.tool_intelligence.urls")),

    path("admin/tool-scores/", include(tool_scores_urlpatterns)),

    path("admin/command-center/", include(command_center_urls)),

    path("admin/email/", include(email_admin_urls)),

    path("admin/experiments/", include(experiments_admin_urls)),

    path("admin/marketplace/", include(marketplace_admin_urls)),

    path("admin/revenue/", include(monetization_admin_urls)),

    path("admin/campaigns/", include("apps.campaigns.urls")),

    path("admin/push/", include(common_push_urls.admin_urlpatterns)),

    path("admin/growth-agent/", include("apps.growth_agent.urls")),

    path("admin/moderation/", include("apps.engagement.moderation_urls")),

    path("admin/workflows/", include(workflows_admin_urls)),

    path("admin/creator/", include(creator_admin_urls)),

    path("admin/launch-readiness/", include("apps.launch_readiness.urls")),

    path("admin/referrals/", include(referrals_admin_urls)),

    path("admin/competitors/", include("apps.competitor_intel.urls")),

    path("admin/backlinks/", include("apps.backlinks.urls")),

    path("ai/", include("apps.ai_providers.urls")),

    path("jobs/", include("apps.jobs.urls")),

    path("marketplace/", include("apps.marketplace.urls")),

    path("newsletter/", include("apps.email_growth.urls")),

    path("experiments/", include("apps.experiments.urls")),

    path("programmatic/", include("apps.programmatic_seo.urls")),

    path("engagement/", include("apps.engagement.urls")),

    path("community/", include("apps.engagement.community_urls")),

    path("workflows/", include("apps.workflows.urls")),

    path("creator/", include("apps.creator_hub.urls")),

    path("referrals/", include("apps.referrals.urls")),

    path("gamification/", include("apps.gamification.urls")),

    path("assistant/", include("apps.assistant.urls")),

    path("content/", include("apps.content_factory.urls")),

    path("monetization/", include("apps.monetization.urls")),

    path("push/", include("apps.common.push_urls")),

    path("mobile/", include("apps.tools_registry.mobile_urls")),

    path("t/", include("apps.tools_registry.tool_urls")),

]

