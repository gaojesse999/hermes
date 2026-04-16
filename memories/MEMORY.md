User's Hermes environment uses /root/.hermes/config.yaml with platform_toolsets configured; current active platform in chat is weixin, whose default toolset is hermes-weixin, while RTK was installed at /root/.local/bin/rtk and Hermes supports user plugins under /root/.hermes/plugins/.
§
Current Hermes profile has a user plugin at /root/.hermes/plugins/rtk_terminal that registers an rtk_terminal tool, injects pre_llm guidance to prefer it, and blocks direct terminal calls so shell execution routes through RTK.
§
User asked to restart the Hermes gateway after RTK plugin changes so the updated plugin behavior takes effect immediately; gateway restart is a relevant post-plugin-change step in this profile.