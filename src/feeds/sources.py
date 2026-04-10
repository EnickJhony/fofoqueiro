from src.config.settings import Settings



def get_feed_sources(settings: Settings) -> list[str]:
    return settings.rss_sources
